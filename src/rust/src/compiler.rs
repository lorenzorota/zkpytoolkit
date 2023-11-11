use pyo3::prelude::*;
// use pyo3::types::IntoPyDict;
// use pyo3::ToPyObject;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

pub(crate) fn create_submodule(py: pyo3::Python<'_>) -> pyo3::PyResult<&pyo3::prelude::PyModule> {
    let submod = pyo3::prelude::PyModule::new(py, "compiler")?;
    submod.add_function(pyo3::wrap_pyfunction!(sum_as_string, submod)?)?;
    Ok(submod)
}