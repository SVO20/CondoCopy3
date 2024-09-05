"""
Tool: ClassMixer

This module provides a dynamic mechanism to mix multiple mixins into a base class, handling
initialization and method resolution automatically. It constructs the resulting class by
invoking the __init__ methods of all classes according to the Method Resolution Order (MRO)
and detects if any base class methods are overridden by the mixins.

Key features:
- Dynamically creates a class that inherits from a base class and multiple mixins.
- Automatically calls __init__ for all classes in the MRO, ensuring proper initialization
  order.
- Verifies that none of the base class methods (except __init__) are overridden by the
  mixins.
- Provides a flexible API to either create a mixed class or directly instantiate it with
  arguments.

Usage examples:

1. To create a mixed class:
   MixedItemClass = ClassMixer(BaseClass, MixinOne, MixinTwo)

2. To directly create an instance of the mixed class:
   item = ClassMixer(BaseClass, MixinOne, MixinTwo)(*args, **kwargs)

Functionality in detail:

- Base class and mixins type validation: Ensures that only valid class types are passed as
  arguments.
- Mixin __init__ validation: Mixins are expected not to require initialization arguments,
  and this is enforced by the module.
- Method override check: Detects any method overrides in the mixins, preventing unintentional
  method conflicts between the base class and the mixins.
- Flexible API: Either returns a new mixed class or an instance, depending on whether arguments
  are passed during invocation.

Error handling:
- Raises TypeError if any of the provided base class or mixins are not valid classes.
- Raises TypeError if any mixin has an __init__ method that expects arguments.
- Raises TypeError if methods from the base class (except __init__) are overridden by the mixins.

/GPT-assisted docstring/"""

from typing import Type, Any

from logger import trace, error


def ClassMixer(base_class: Type[Any], *mixins: Type[Any]) -> Type[Any]:
    """
    Creates a new class combining a base class and multiple mixins, with
    automatic initialization and method override checking.

    Args:
        base_class (type): The base class to extend.
        *mixins (types): One or more mixin classes to combine with the base class.

    Returns:
        A function that can either return the mixed class or create an instance
        of it, depending on whether arguments are passed.

    Raises:
        TypeError: If any of the provided base_class or mixins are not classes.
        TypeError: If any mixin's __init__ method requires arguments.
    """
    # Type check for base class
    if not isinstance(base_class, type):
        raise TypeError(f"Expected base_class to be a class, got {type(base_class).__name__}")

    # Type check for each mixin
    for mixin in mixins:
        if not isinstance(mixin, type):
            raise TypeError(f"Expected mixins to be classes, but got {type(mixin).__name__}")

    # Ensure mixins' __init__ methods do not require arguments
    for mixin in mixins:
        if '__init__' in mixin.__dict__:  # Check if mixin has its own __init__
            init_method = mixin.__dict__['__init__']
            if init_method.__code__.co_argcount > 1:  # More than 'self' means it expects arguments
                raise TypeError(
                    f"The mixin {mixin.__name__} has an __init__ method that requires arguments, but no arguments are allowed.")

    # Compose new classname
    mixin_names = 'Mix'.join([mix.__name__ for mix in mixins])
    new_class_name = f"{base_class.__name__}Mix{mixin_names}"

    # Create a new class that inherits from all mixins and the base class
    class MixedClass(*mixins, base_class):
        def __init__(self, *args, **kwargs):
            # Automatically check for method overrides before initialization
            self.check_overrides()

            # Iterate through the MRO and call the `__init__` for each class
            for cls in self.__class__.__mro__:
                if cls is not MixedClass and hasattr(cls, '__init__'):
                    if cls is base_class:  # Pass arguments only to the base_class
                        try:

                            # Initialize base class with args
                            cls.__init__(self, *args, **kwargs)
                            trace(f"{cls.__name__}.__init__ called with arguments: {args}, {kwargs}")

                        except TypeError as e:
                            error(f"TypeError in {cls.__name__}.__init__: "
                                  f"Incorrect argument types passed to base class. "
                                  f"Args: {args}, Kwargs: {kwargs}. Error: {e}")
                            raise TypeError(f"TypeError in {cls.__name__}.__init__: "
                                            f"Incorrect argument types passed to base class. "
                                            f"Args: {args}, Kwargs: {kwargs}. Error: {e}")
                        except ValueError as e:
                            error(f"ValueError in {cls.__name__}.__init__: "
                                  f"Invalid argument values passed to base class. "
                                  f"Args: {args}, Kwargs: {kwargs}. Error: {e}")
                            raise ValueError(f"ValueError in {cls.__name__}.__init__: "
                                             f"Invalid argument values passed to base class. "
                                             f"Args: {args}, Kwargs: {kwargs}. Error: {e}")
                        except Exception as e:
                            error(f"Unexpected error in {cls.__name__}.__init__: "
                                  f"Failed to initialize base class with "
                                  f"args: {args}, kwargs: {kwargs}. Error: {e}")
                            raise Exception(f"Unexpected error in {cls.__name__}.__init__: "
                                            f"Failed to initialize base class with "
                                            f"args: {args}, kwargs: {kwargs}. Error: {e}")
                    else:
                        try:

                            # Initialize mixin without args
                            cls.__init__(self)
                            trace(f"{cls.__name__}.__init__ called without arguments")

                        except TypeError as e:
                            error(f"TypeError in {cls.__name__}.__init__: Mixin initialization "
                                  f"failed due to incorrect argument types. No args expected. "
                                  f"Error: {e}")
                            raise TypeError(f"TypeError in {cls.__name__}.__init__: "
                                            f"Mixin initialization failed due to incorrect "
                                            f"argument types. No args expected. Error: {e}")
                        except ValueError as e:
                            error(f"ValueError in {cls.__name__}.__init__: "
                                  f"Mixin initialization failed due to invalid values, "
                                  f"though no args were passed. Error: {e}")
                            raise ValueError(f"ValueError in {cls.__name__}.__init__: "
                                             f"Mixin initialization failed due to invalid values, "
                                             f"though no args were passed. Error: {e}")
                        except Exception as e:
                            error(f"Unexpected error in {cls.__name__}.__init__: "
                                  f"Failed to initialize mixin. No args expected. Error: {e}")
                            raise Exception(f"Unexpected error in {cls.__name__}.__init__: "
                                            f"Failed to initialize mixin. No args expected. Error: {e}")

        @classmethod
        def check_overrides(cls):
            """
            Checks if any methods from the base class have been overridden
            by the mixins.

            Raises:
                TypeError: If any methods from the base class are found to be
                overridden by the mixins.
            """
            base_methods = {name: func
                            for name, func
                            in base_class.__dict__.items() if callable(func)}
            overridden_methods = []

            for name, base_method in base_methods.items():
                current_method = getattr(cls, name, None)
                if current_method is not base_method:
                    overridden_methods.append(name)

            # __init__ is excluded because all __init__ methods
            # from the mixins and, finally, the base class -- are expected to execute sequentially
            overridden_methods = [method for method in overridden_methods if method != '__init__']
            if overridden_methods:
                error(f'The following base class methods were overridden: {overridden_methods}')
                raise TypeError(
                    f"The following base class methods were overridden: {overridden_methods}")
            else:
                trace("All base class methods are preserved and not overridden.")

    # Naming the class
    MixedClass.__name__ = new_class_name

    # Directly return the class itself
    return MixedClass

# # ====== Test cases to check the behavior of ClassMixer and mixed classes =========
#
# # Test 1: Ensure proper initialization of base class and mixins
# def test_initialization():
#     class BaseClass:
#         def __init__(self, name):
#             self.name = name
#             print(f"BaseClass initialized with name: {self.name}")
#
#     class MixinOne:
#         def __init__(self, *args, **kwargs):
#             print("MixinOne initialized")
#
#     class MixinTwo:
#         def __init__(self, *args, **kwargs):
#             print("MixinTwo initialized")
#
#     # Create and initialize an instance directly
#     item = ClassMixer(BaseClass, MixinOne, MixinTwo)("TestItem")
#
#     assert item.name == "TestItem", "BaseClass was not initialized with the correct name"
#
#
# # Test 2: Check method override conflict detection
# def test_override_conflict():
#     class BaseClass:
#         def process(self):
#             print("Processing base class")
#
#     class MixinOne:
#         def process(self):
#             print("MixinOne process method")
#
#     try:
#         # This should raise a TypeError due to method override
#         ClassMixer(BaseClass, MixinOne)()
#     except TypeError as e:
#         assert "overridden" in str(e), "Method override conflict was not detected"
#
#
# # Test 3: Check mixins without __init__ arguments
# def test_mixin_no_args_init():
#     class BaseClass:
#         def __init__(self, name):
#             self.name = name
#             print(f"BaseClass initialized with name: {self.name}")
#
#     class MixinOne:
#         def __init__(self):
#             print("MixinOne initialized without args")
#
#     # No arguments passed to mixins, only to the base class
#     item = ClassMixer(BaseClass, MixinOne)("TestItem")
#     assert item.name == "TestItem", "BaseClass was not initialized with the correct name"
#
#
# # Test 4: Ensure no arguments passed to mixins that require none
# def test_mixin_with_init_args_error():
#     class BaseClass:
#         def __init__(self, name):
#             self.name = name
#
#     class MixinOne:
#         def __init__(self, extra_arg):
#             print("This mixin should not accept arguments")
#
#     try:
#         # This should raise a TypeError because the mixin expects arguments
#         item = ClassMixer(BaseClass, MixinOne)("TestItem")
#     except TypeError as e:
#         assert "requires arguments" in str(e), "Mixin __init__ argument check failed"
#
#
# # Test 5: Ensure that ClassMixer returns a class if no arguments are passed
# def test_return_class():
#     class BaseClass:
#         pass
#
#     class MixinOne:
#         pass
#
#     MixedClass = ClassMixer(BaseClass, MixinOne)
#     assert issubclass(MixedClass, BaseClass), "ClassMixer did not return the correct class"
#
#
# # Test 6: Ensure that ClassMixer returns an instance if arguments are present
# def test_return_instance():
#     class BaseClass:
#         def __init__(self, name):
#             self.name = name
#
#     class MixinOne:
#         pass
#
#     class MixinTwo:
#         pass
#
#     # Create an instance of the mixed class
#     mixed_instance = ClassMixer(BaseClass, MixinOne, MixinTwo)("TestItem")
#
#     # Ensure that mixed_instance is an instance of BaseClass, MixinOne, and MixinTwo
#     assert isinstance(mixed_instance,
#                       BaseClass), "ClassMixer did not return an instance of BaseClass"
#     assert mixed_instance.name == "TestItem", "BaseClass was not initialized with the correct name"
#     assert isinstance(mixed_instance,
#                       MixinOne), "ClassMixer did not return an instance of MixinOne"
#     assert isinstance(mixed_instance,
#                       MixinTwo), "ClassMixer did not return an instance of MixinTwo"
#
#
# # Run tests
# test_initialization()
# test_override_conflict()
# test_mixin_no_args_init()
# test_mixin_with_init_args_error()
# test_return_class()
# test_return_instance()
#
# print("All tests passed.")
