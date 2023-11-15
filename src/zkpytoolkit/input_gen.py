import inspect
import textwrap
from zkpytoolkit.types import Public, Private, Array, field

def contains_field_recursive(arg_type):
    if arg_type == field:
        return True
    elif getattr(arg_type, "__origin__", None) in {Private, Public}:
        inner_type = arg_type.__args__[0]
        return contains_field_recursive(inner_type)
    elif getattr(arg_type, "__origin__", None) == Array:
        inner_type = arg_type.__args__[0]
        return contains_field_recursive(inner_type)
    else:
        return False

def parse_argument_value(value, arg_type, prefix=''):
    if getattr(arg_type, "__origin__", None) in {Private, Public}:
        inner_type = arg_type.__args__[0]
        return parse_argument_value(value, inner_type, f'{prefix}')
    elif arg_type == int:
        return f'({prefix} #x{value:08x})'
    elif arg_type == field:
        return f'({prefix} #f{value})'
    elif arg_type == bool:
        return f'({prefix} true)' if value else f'({prefix} false)'
    elif getattr(arg_type, "__origin__", None) == Array:
        inner_type = arg_type.__args__[0]
        result = []
        if getattr(inner_type, "__origin__", None) == Array:  # Check if it's a nested array
            for i, inner_value in enumerate(value):
                inner_prefix = f'{prefix}.{i}'
                inner_values = parse_argument_value(inner_value, inner_type, inner_prefix)
                result.append(f'{inner_values}')
        else:
            for i, inner_value in enumerate(value):
                inner_prefix = f'{prefix}.{i}'
                inner_values = parse_argument_value(inner_value, inner_type, inner_prefix)
                result.append(f'{inner_values}')

        return '\n'.join(result)
    else:
        return str(value)

def prepare_prover_inputs(argument_names, argument_types, modulus, field_tmp, *args, **kwargs):
    global field
    field = field_tmp

    # Get argument values
    argument_values = args + tuple(kwargs.values())

    # Create a dictionary with argument names, values, and type annotations
    arguments_info = {
        name: (value, argument_types.get(name, None))
        for name, value in zip(argument_names, argument_values)
    }

    # Generate Lisp code
    lisp_code = "(let (\n"
    for name, (value, arg_type) in arguments_info.items():
        parsed_value = parse_argument_value(value, arg_type, name)
        lisp_code += textwrap.indent(parsed_value, "    ") + "\n"
    lisp_code += ")\n    false\n)"

     # Wrap the Lisp code inside (set_default_modulus ...) if any argument type is field
    contains_field = any(contains_field_recursive(arg_type) for arg_type in argument_types.values())
    if contains_field:
        lisp_code = textwrap.indent(lisp_code, "    ") + "\n"
        lisp_code = f"(set_default_modulus {modulus}\n{lisp_code})"

    return lisp_code

def prepare_verifier_inputs(argument_names, argument_types, return_type, modulus, return_value, field_tmp, *args, **kwargs):
    global field
    field = field_tmp

    # Get argument values
    argument_values = args + tuple(kwargs.values())

    # Create a dictionary with argument names, values, and type annotations
    arguments_info = {
        name: (value, argument_types.get(name, None))
        for name, value in zip(argument_names, argument_values)
    }

    # Create a dictionary with return value and type annotation
    return_info = {
        'return': (return_value, return_type)
    }
    
    # Generate Lisp code
    lisp_code = "(let (\n"
    # First parse all public values
    for name, (value, arg_type) in arguments_info.items():
        if getattr(arg_type, "__origin__", None) == Private:
            continue  # Skip the iteration if arg_type is Private
    
        parsed_value = parse_argument_value(value, arg_type, name)
        lisp_code += textwrap.indent(parsed_value, "    ") + "\n"
    # Then parse return value and type
    return_value, return_type = return_info.get('return', (None, None))
    parsed_return = parse_argument_value(return_value, return_type, 'return')
    lisp_code += textwrap.indent(parsed_return, "    ") + "\n"
    # Finally close the lisp
    lisp_code += ")\n    false\n)"
    
    # Wrap the Lisp code inside (set_default_modulus ...) if any argument type is field
    contains_field = any(contains_field_recursive(arg_type) for arg_type in argument_types.values())
    if contains_field:
        lisp_code = textwrap.indent(lisp_code, "    ") + "\n"
        lisp_code = f"(set_default_modulus {modulus}\n{lisp_code})"

    return lisp_code

def represent_object(obj, alias=None):
    module = inspect.getmodule(obj)
    if module is None:
        return ""
    else:
        module_name = module.__name__
    obj_name = obj.__name__
    
    if hasattr(obj, '__class__') and obj.__class__.__name__ == 'module':
        # If the object is a module, just return the import statement for the module
        return f"import {module_name}"
    elif inspect.isfunction(obj) and module_name == "__main__":
        # If the object is a function, return its implementation
        source_lines, _ = inspect.getsourcelines(obj)
        function_impl = ''.join(source_lines)
        return '\n' + function_impl
    else:
        if alias is None or obj_name == alias:
            # If no alias provided or obj_name is the same as alias, use a simple import statement
            import_statement = f"from {module_name} import {obj_name}"
        else:
            # If alias is provided and different from obj_name, use "as alias" in the import statement
            import_statement = f"from {module_name} import {obj_name} as {alias}"
    
    return import_statement

def process_includes(obj_list):
    result = []
    
    for item in obj_list:
        if isinstance(item, tuple):
            # If item is a pair, pass it as (obj, alias) to parse_include
            obj, alias = item
            result.append(represent_object(obj, alias))
        else:
            # If item is not a pair, pass it as obj to parse_include
            result.append(represent_object(item))
    
    # Concatenate the results with a newline in between
    return '\n'.join(result)