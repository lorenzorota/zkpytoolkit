use pyo3::prelude::*;

use circ::ir::{opt::Opt, opt::opt, term::Computations};
use circ_opt::CircOpt;
use circ::cfg::cfg;
use zkpyc::export::write_constraints;
use zkpyc::front::{self, Mode::Proof, FrontEnd, python::Inputs};
use zkpyc::utilities::r1cs::{ProverData, VerifierData};
use zkpyc::utilities::{opt::reduce_linearities, trans::to_r1cs};
use zkpyc::utilities::scalar_fields::bls12_381::Bls12_381;
use zkpyc::utilities::scalar_fields::bn256::Bn256;
use curve25519_dalek::scalar::Scalar as Curve25519;
use std::fs::{File, remove_file};
use std::io::Write;
use std::path::{Path, PathBuf};

use crate::ff_constants::*;

// use pyo3::types::IntoPyDict;
// use pyo3::ToPyObject;

enum Modulus {
    Integer(rug::Integer)
}

fn optimize_computations(cs: Computations) -> Computations {
    let mut opts = Vec::new();

    opts.push(Opt::ScalarizeVars);
    opts.push(Opt::Flatten);
    opts.push(Opt::Sha);
    opts.push(Opt::ConstantFold(Box::new([])));
    opts.push(Opt::ParseCondStores);
    // Tuples must be eliminated before oblivious array elim
    opts.push(Opt::Tuple);
    opts.push(Opt::ConstantFold(Box::new([])));
    opts.push(Opt::Tuple);
    opts.push(Opt::Obliv);
    // The obliv elim pass produces more tuples, that must be eliminated
    opts.push(Opt::Tuple);
    // The following optimizations are run when the ram option is enabled
    // We will assume it is true by default because cfg() does not expose
    // CircOpt yet (it is still private), and a workaround isn't worth it.
    opts.push(Opt::PersistentRam);
    opts.push(Opt::VolatileRam);
    opts.push(Opt::SkolemizeChallenges);
    opts.push(Opt::LinearScan);
    // The linear scan pass produces more tuples, that must be eliminated
    opts.push(Opt::Tuple);
    opts.push(Opt::Flatten);
    opts.push(Opt::ConstantFold(Box::new([])));
    opt(cs, opts)
}

fn run_zkpyc_compiler(
    f_name: &String,
    inputs: Inputs,
) -> PyResult<(ProverData, VerifierData, usize)> {    
    let cs = front::python::PythonFE::gen(inputs);
    let cs = optimize_computations(cs);
    let cs = cs.get(f_name);
    let mut r1cs = to_r1cs(cs, cfg());
    r1cs = reduce_linearities(r1cs, cfg());
    let constraints_count = r1cs.constraints().len();
    let (prover_data, verifier_data) = r1cs.finalize(cs);
    Ok((prover_data, verifier_data, constraints_count))
}

#[pyfunction]
#[pyo3(signature = (
    modulus="52435875175126190479447740508185965837690552500527637822603658699938581184513",
))]
fn init(modulus: &str) -> PyResult<()> {
    let mut circ_options = CircOpt::default();
    circ_options.field.custom_modulus = String::from(modulus);
    // We will make the circ_options customizable in the future.
    circ::cfg::set(&circ_options);
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (f_name, input))]
fn compile(
    f_name: String,
    input: String,
) -> PyResult<usize> {
    let file_path = Path::new(".").join(PathBuf::from(format!(".__def_{}.py", f_name)));
    let mut file = File::create(&file_path)?;
    // Because of how the compiler is written, we need to temporarily
    // store source code as a file.
    file.write_all(input.as_bytes())?;

    let inputs = front::python::Inputs {
        file: file_path.clone(),
        entry_point: f_name.clone(),
        mode: Proof,
    };

    // Remove temporary function definition file.
    let (pd, vd, constr_count) = match run_zkpyc_compiler(&f_name, inputs) {
        Ok((pd, vd, constr_count)) => {
            remove_file(&file_path)?;
            (pd, vd, constr_count)
        }
        Err(err) => {
            remove_file(&file_path)?;
            return Err(err);
        },
    };

    match Modulus::Integer(cfg().field().modulus().clone()) {
        Modulus::Integer(i) if i == get_bls12_381_const() => write_constraints::<Bls12_381>(&pd.r1cs, &f_name),
        Modulus::Integer(i) if i == get_bn256_const() => write_constraints::<Bn256>(&pd.r1cs, &f_name),
        Modulus::Integer(i) if i == get_curve25519_const() => write_constraints::<Curve25519>(&pd.r1cs, &f_name),
        _ => panic!("Prime field modulus not supported. The currently supported scalar fields are those of the BLS12_381, BN256 and Curve25519 curves."),
    }

    Ok(constr_count)
}


pub(crate) fn create_submodule(py: pyo3::Python<'_>) -> pyo3::PyResult<&pyo3::prelude::PyModule> {
    let submod = pyo3::prelude::PyModule::new(py, "compiler")?;
    submod.add_function(pyo3::wrap_pyfunction!(init, submod)?)?;
    submod.add_function(pyo3::wrap_pyfunction!(compile, submod)?)?;
    Ok(submod)
}
