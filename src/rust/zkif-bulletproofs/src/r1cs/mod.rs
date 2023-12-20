
mod notes {}

mod constraint_system;
mod linear_combination;
mod proof;
mod prover;
mod verifier;
pub mod zkinterface_backend;

pub use self::constraint_system::ConstraintSystem;
pub use self::linear_combination::{LinearCombination, Variable};
pub use self::proof::R1CSProof;
pub use self::prover::Prover;
pub use self::verifier::Verifier;

pub use errors::R1CSError;
