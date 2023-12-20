use bellman::ConstraintSystem;
use pairing::bls12_381::{Bls12, Fr, FrRepr};
use sapling_crypto::circuit::num::AllocatedNum;
use std::env;
use crate::import::call_gadget;
use bellman::gadgets::test::TestConstraintSystem;
use super::exec_zokrates::exec_zokrates;

#[test]
fn test_import_from_zokrates() {
    /*
        a^2 + b^2 == c^2
    */

    if env::var("ZOKRATES_HOME").is_err() {
        println!("No ZOKRATES_HOME in environment, skipping demo_import_from_zokrates");
        return;
    }

    use ff::PrimeField;

    let mut cs = TestConstraintSystem::<Bls12>::new();
    let one = TestConstraintSystem::<Bls12>::one();
    let zero = {
        let x = Fr::from_repr(FrRepr::from(0)).unwrap();
        AllocatedNum::alloc(cs.namespace(|| "zero"), || Ok(x)).unwrap()
    };

    let a = {
        let x = Fr::from_repr(FrRepr::from(3)).unwrap();
        AllocatedNum::alloc(cs.namespace(|| "a"), || Ok(x)).unwrap()
    };
    let b = {
        let x = Fr::from_repr(FrRepr::from(4)).unwrap();
        AllocatedNum::alloc(cs.namespace(|| "b"), || Ok(x)).unwrap()
    };
    let c = {
        let x = Fr::from_repr(FrRepr::from(5)).unwrap();
        AllocatedNum::alloc(cs.namespace(|| "c"), || Ok(x)).unwrap()
    };

    let a2_b2 = call_gadget(
        &mut cs.namespace(|| "a2 + b2"),
        &[a, b],
        &exec_zokrates,
    ).unwrap();

    let c2 = call_gadget(
        &mut cs.namespace(|| "c2 + zero2"),
        &[c, zero.clone()],
        &exec_zokrates,
    ).unwrap();

    println!("a2 + b2 = {}", a2_b2[0].get_value().unwrap().into_repr());
    println!("     c2 = {}", c2[0].get_value().unwrap().into_repr());
    assert_eq!(a2_b2.len(), 1);
    assert_eq!(c2.len(), 1);

    cs.enforce(|| "a2 + b2 = c2 + zero2",
               |lc| lc + one,
               |lc| lc + a2_b2[0].get_variable(),
               |lc| lc + c2[0].get_variable(),
    );

    cs.enforce(|| "zero = 0",
               |lc| lc + one,
               |lc| lc + zero.get_variable(),
               |lc| lc,
    );

    println!("{}", cs.pretty_print());
    assert!(cs.is_satisfied());
    assert_eq!(cs.num_constraints(), 3 + 3 + 1 + 1);
}
