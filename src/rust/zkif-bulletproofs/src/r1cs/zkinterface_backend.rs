//! A zkInterface backend using Bulletproofs.

extern crate curve25519_dalek;
extern crate merlin;
extern crate rand;
extern crate zkinterface;

use self::zkinterface::{
    Result, Reader, consumers::reader::Term,
};
use curve25519_dalek::scalar::Scalar;
use errors::R1CSError;
use failure::Fail;
use merlin::Transcript;
use r1cs::ConstraintSystem;
use r1cs::LinearCombination;
use r1cs::Prover;
use r1cs::R1CSProof;
use r1cs::Variable;
use r1cs::Verifier;
use std::cmp::min;
use std::collections::HashMap;
use BulletproofGens;
use PedersenGens;

/// Generate a proof using zkInterface messages:
/// - `Circuit` contains the public inputs.
/// - `R1CSConstraints` contains an R1CS which we convert to an arithmetic circuit on the fly.
/// - `Witness` contains the values to assign to all variables.
pub fn prove(messages: &Reader, generators_count: usize) -> Result<R1CSProof> {
    // Common
    let pc_gens = PedersenGens::default();
    let bp_gens = BulletproofGens::new(generators_count, 1);
    let mut transcript = Transcript::new(b"zkInterfaceGadget");
    // /Common

    // 1. Create a prover
    let prover = Prover::new(&bp_gens, &pc_gens, &mut transcript);

    // 2. There are no high-level variables.

    // 3. Build a CS
    let mut cs = prover.finalize_inputs();

    gadget_from_messages(&mut cs, messages, true)?;

    // 4. Make a proof
    let proof = cs.prove().map_err(|e| e.compat())?;

    Ok(proof)
}

/// Verify a proof using zkInterface messages:
/// - `Circuit` contains the public inputs.
/// - `R1CSConstraints` contains an R1CS which we convert to an arithmetic circuit on the fly.
pub fn verify(messages: &Reader, proof: &R1CSProof, generators_count: usize) -> Result<bool> {
    // Common
    let pc_gens = PedersenGens::default();
    let bp_gens = BulletproofGens::new(generators_count, 1);
    let mut transcript = Transcript::new(b"zkInterfaceGadget");
    // /Common

    // 1. Create a verifier
    let verifier = Verifier::new(&bp_gens, &pc_gens, &mut transcript);

    // 2. There are no high-level variables.

    // 3. Build a CS
    let mut cs = verifier.finalize_inputs();

    gadget_from_messages(&mut cs, messages, false)?;

    // 4. Verify the proof
    match cs.verify(&proof) {
        Ok(_) => Ok(true),
        Err(_) => Ok(false),
    }
}

/// A gadget using a circuit in zkInterface messages.
pub fn gadget_from_messages<CS: ConstraintSystem>(
    cs: &mut CS,
    messages: &Reader,
    prover: bool,
) -> Result<()> {
    let public_vars = messages
        .instance_variables()
        .ok_or("Missing Circuit.connections")?;

    let private_vars = messages
        .private_variables()
        .ok_or("Missing Circuit.connections")?;

    // Map zkif variables to Bulletproofs's equivalent, LinearCombination.
    let mut id_to_lc = HashMap::<u64, LinearCombination>::new();

    // Prover tracks the values assigned to zkif variables in order to evaluate the gates.
    let mut id_to_value = HashMap::<u64, Scalar>::new();

    // Map constant one.
    id_to_lc.insert(0, Variable::One().into());
    if prover {
        id_to_value.insert(0, Scalar::one());
    }

    // Map public inputs.
    for var in public_vars {
        let val = scalar_from_zkif(var.value)?;
        id_to_lc.insert(var.id, val.into());

        if prover {
            id_to_value.insert(var.id, val);
        }

        // eprintln!("public{} = {:?}", var.id, val);
    }
    // eprintln!();

    // Map witness (if prover).
    if prover {
        for var in private_vars.iter() {
            let val = scalar_from_zkif(var.value)?;
            id_to_value.insert(var.id, val);

            // eprintln!("private{} = {:?}", var.id, val);
        }
        // eprintln!();
    }

    // Step 1: Allocate one mult gate per R1CS constraint.
    let mut gates_a = vec![];
    let mut gates_b = vec![];
    let mut gates_c = vec![];

    for constraint in messages.iter_constraints() {
        let (gate_a, gate_b, gate_c) = cs
            .allocate(|| {
                Ok((
                    // Prover evaluates the incoming linear combinations using the witness.
                    eval_zkif_lc(&id_to_value, &constraint.a),
                    eval_zkif_lc(&id_to_value, &constraint.b),
                    eval_zkif_lc(&id_to_value, &constraint.c),
                ))
            })
            .map_err(|e| e.compat())?;

        gates_a.push(gate_a);
        gates_b.push(gate_b);
        gates_c.push(gate_c);

        // XXX: If constraint.a/b/c is just x, insert id_to_lc[x.id] = gate_var
    }

    // Step 2: Allocate extra gates for variables that are not yet defined.
    for circuit_var in private_vars.iter() {
        if !id_to_lc.contains_key(&circuit_var.id) {
            let (gate_var, _, _) = cs
                .allocate(|| {
                    // Prover takes the value from witness.
                    let val = id_to_value.get(&circuit_var.id);
                    Ok((
                        val.unwrap().clone(),
                        Scalar::zero(), // Dummy.
                        Scalar::zero(), // Dummy.
                    ))
                })
                .map_err(|e| e.compat())?;

            id_to_lc.insert(circuit_var.id, gate_var.into());
            // eprintln!("private{} allocated to {:?}", circuit_var.id, gate_var);
        }
    }
    // eprintln!();

    // Step 3: Add linear constraints into each wire of each gate.
    for (i, constraint) in messages.iter_constraints().enumerate() {
        // eprintln!("constraint {}:", i);

        let lc_a = convert_zkif_lc(&id_to_lc, &constraint.a)?;
        // eprintln!("  A = {:?}", lc_a);
        cs.constrain(lc_a - gates_a[i]);

        let lc_b = convert_zkif_lc(&id_to_lc, &constraint.b)?;
        // eprintln!("  B = {:?}", lc_b);
        cs.constrain(lc_b - gates_b[i]);

        let lc_c = convert_zkif_lc(&id_to_lc, &constraint.c)?;
        // eprintln!("  C = {:?}", lc_c);
        cs.constrain(lc_c - gates_c[i]);

        // eprintln!();
        // XXX: Skip trivial constraints where the lc was defined as just the gate var.
    }

    // XXX: optimize gate allocation.
    // - Detect trivial LC wires = 1 * x. Then use the gate wire as variable x.
    //   Skip dummy allocation in step 2, and skip constraint in step 3.
    // - Detect when the LC going into a gate contains a single new variable 1.x,
    //   set x = wire - (other terms in existing variables).
    // - Allocate two variables at once (left, right, ignore output)?
    // - Try to reorder the constraints to minimize dummy gates allocations.

    Ok(())
}

/// This is a gadget equivalent to the zkinterface example circuit: x^2 + y^2 = zz
fn _example_gadget<CS: ConstraintSystem>(cs: &mut CS) -> Result<()> {
    let x = LinearCombination::from(3 as u64);
    let y = LinearCombination::from(4 as u64);
    let zz = LinearCombination::from(25 as u64);

    let (_, _, xx) = cs.multiply(x.clone(), x);
    let (_, _, yy) = cs.multiply(y.clone(), y);

    cs.constrain(xx + yy - zz);

    Ok(())
}

/// Convert zkInterface little-endian bytes to Dalek Scalar.
fn scalar_from_zkif(le_bytes: &[u8]) -> Result<Scalar> {
    let mut bytes32 = [0; 32];
    let l = min(le_bytes.len(), 32);
    bytes32[..l].copy_from_slice(&le_bytes[..l]);
    Scalar::from_canonical_bytes(bytes32).ok_or("Invalid scalar encoding".into())
}

fn convert_zkif_lc(
    id_to_lc: &HashMap<u64, LinearCombination>,
    zkif_terms: &[Term],
) -> Result<LinearCombination> {
    let mut lc = LinearCombination::default();

    for term in zkif_terms {
        let var = id_to_lc
            .get(&term.id)
            .ok_or(format!("Unknown var {}", term.id))?;
        let coeff = scalar_from_zkif(term.value)?;
        lc = lc + (var.clone() * coeff);
    }

    Ok(lc)
}

fn eval_zkif_lc(id_to_value: &HashMap<u64, Scalar>, terms: &[Term]) -> Scalar {
    terms
        .iter()
        .map(|term| {
            let val = match id_to_value.get(&term.id) {
                Some(s) => s.clone(),
                None => Scalar::zero(),
            };
            let coeff = scalar_from_zkif(term.value).unwrap();
            coeff * val
        })
        .sum()
}

#[test]
fn test_zkinterface_backend() {
    use self::zkinterface::producers::examples;

    // Load test messages common to the prover and verifier: Circuit and Constraints.
    let verifier_messages = {
        let mut buf = Vec::<u8>::new();
        examples::example_circuit_header().write_into(&mut buf).unwrap();
        examples::example_constraints().write_into(&mut buf).unwrap();
        let mut msg = Reader::new();
        msg.push_message(buf).unwrap();
        msg
    };

    // Prover uses an additional message: Witness.
    let prover_messages = {
        let mut msg = verifier_messages.clone();
        let mut buf = Vec::<u8>::new();
        examples::example_witness().write_into(&mut buf).unwrap();
        msg.push_message(buf).unwrap();
        msg
    };

    // Prove using the witness.
    let proof = prove(&prover_messages, 128).unwrap();

    // Verify using the circuit and the proof.
    verify(&verifier_messages, &proof, 128).unwrap();
}
