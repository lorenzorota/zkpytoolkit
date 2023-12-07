from zkpytoolkit.types import _set_modulus
from zkpytoolkit.input_gen import prepare_prover_inputs, prepare_verifier_inputs, process_includes, represent_object
from zkpytoolkit.hazmat.bindings import compiler

class ZKP:
    _instance = None
    modulus = None
    field = None # this is a temporary solution for type checking in externally called functions

    def __new__(cls, modulus=None):
        if cls._instance is None:
            cls._instance = super(ZKP, cls).__new__(cls)
            field = _set_modulus(modulus)
            compiler.init(str(field.modulus))
            cls.modulus = field.modulus
            cls.field = field
        else:
            raise RuntimeError("Only one instance of the ZKP class is allowed.")
        return cls._instance

    def compile(self, func, includes=None, global_vars=None):
        # Get the function implementation and name
        func_impl = represent_object(func)
        func_name = func.__name__

        # Get the processed objects
        if includes is None:
            obj_impl = ""
        else:
            obj_impl = process_includes(includes, self.field, global_vars)
        
        # Concatenate the function definition and processed objects
        code = f"{obj_impl}{func_impl}"
        # print(code)
        return compiler.compile(func_name, code)

    def prepare_proof(self, func, *args, **kwargs):
        argument_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        argument_types = func.__annotations__
        lisp_code = prepare_prover_inputs(
            argument_names,
            argument_types,
            self.modulus,
            self.field,
            *args,
            **kwargs
        )

        return compiler.setup_proof(func.__name__, lisp_code)

    def prepare_verification(self, func, *args, return_value=None, **kwargs):
        if return_value is None:
            raise ValueError("Missing return value for verification.")

        argument_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        argument_types = func.__annotations__
        return_type = argument_types.get('return', None)

        lisp_code = prepare_verifier_inputs(
            argument_names,
            argument_types,
            return_type,
            self.modulus,
            return_value,
            self.field,
            *args,
            **kwargs,
        )

        return compiler.setup_verification(func.__name__, lisp_code)
    
    def cleanup(self):
        compiler.cleanup()