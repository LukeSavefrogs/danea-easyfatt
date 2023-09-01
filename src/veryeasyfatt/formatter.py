from collections.abc import Mapping
import enum
import string

COMMANDS_PREFIX = 's'
COMMANDS_SEPARATOR = '->'
class FormatterCommands(enum.Enum):
    UPPER = 'uppercase'
    LOWER = 'lowercase'
    CAPITALIZE = 'capitalize'
    TITLE = 'title'
    SUBSTRING = 'substring'
    REPLACE = 'replace'
    # SUBSTRING = r'^substring\((\s*\d+\s*)+((?<=,)\s*\d+\s*)*\)$' # One mandatory argument, N optional argument

class SimpleFormatter(string.Formatter):
    def __init__(self, allow_attribute_access=False):
        """ Formatter that allows to use user-friendly commands to format strings.

        By default it does not allow to access attributes of variables, but this 
        can be changed by setting `allow_attribute_access` to `True`.
        This choice has been made as a basic security measure to avoid the user to
        access sensitive data.
        See [this blog post](https://lucumr.pocoo.org/2016/12/29/careful-with-str-format/) 
        for more information.

        Args:
            allow_attribute_access (bool, optional): Allow or deny access to variable attributes. Defaults to False.

        Example:
            ```pycon
            >>> unsafe_formatter = UserFormatter(allow_attribute_access=True)
            >>> unsafe_formatter.format('{var[test]}', var={"test": "value"})
            'value'
            >>> safe_formatter = UserFormatter() # by default `allow_attribute_access=False`
            >>> safe_formatter.format('{var[test]}', var={"test": "value"})
            Traceback (most recent call last):
            ...
            Exception: Invalid format string (field name cannot contain "." or "[")
            ```
        """
        self.allow_attribute_access = allow_attribute_access
        super().__init__()

    def get_field(self, field_name, args, kwargs):
        if self.allow_attribute_access == False and ('.' in field_name or '[' in field_name):
            raise Exception('Invalid format string (field name cannot contain "." or "[")')
        
        return super().get_field(field_name, args, kwargs)

    def format_field(self, value, format_spec):
        if isinstance(value, str) and format_spec.startswith(COMMANDS_PREFIX):
            command_stack = [command.strip() for command in format_spec.split(COMMANDS_SEPARATOR)[1:] ]
            format_spec = ""

            for command in command_stack:
                if command == FormatterCommands.UPPER.value:
                    value = value.upper()

                elif command == FormatterCommands.LOWER.value:
                    value = value.lower()
            
                elif command == FormatterCommands.CAPITALIZE.value:
                    value = value.capitalize()

                elif command == FormatterCommands.TITLE.value:
                    value = value.title()
                
                elif command.startswith(FormatterCommands.SUBSTRING.value):
                    if command.count('(') != 1 or command.count(')') != 1:
                        raise ValueError(f"Command '{command}' MUST have parameters")
                    
                    command_args = command.split('(')[1].split(')')[0].split(',')
                    start = int(command_args[0])
                    end = int(command_args[1]) if len(command_args) > 1 else None
                    
                    if end is not None:
                        value = value[start:end]
                    else:
                        value = value[start:]
                
                elif command.startswith(FormatterCommands.REPLACE.value):
                    if command.count('(') != 1 or command.count(')') != 1:
                        raise ValueError(f"Command '{command}' MUST have parameters")
                    
                    command_args = [
                        arg[1:-1] if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")) else arg
                        for arg in (
                            arg.strip() for arg in command.split('(')[1].split(')')[0].split(',')
                        )
                    ]

                    # Remove quotes only if they are at the beginning and at the end of the string
                    # for i, arg in enumerate(command_args):
                    #     if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                    #         command_args[i] = arg[1:-1]

                    search  = str(command_args[0])
                    replace = str(command_args[1])
                    
                    value = value.replace(search, replace)
                
                else:
                    raise ValueError(f'Invalid formatting command {command}')

        return super().format_field(value, format_spec)

SECRET = 'this-is-a-secret'
class Error:
    def __init__(self):
        pass

if __name__ == '__main__':
    f = SimpleFormatter()

    variable = "heLlo WoRld"

    # Results in accessing the globals dictionary of the object and then the value of secret
    # err = Error()
    # print(f.format('{error.__init__.__globals__[SECRET]:s->uppercase}', error = err))
    
    print(f.format('{0:s->uppercase->substring(6)}', variable))
    print(f.format('{0:s->lowercase}', variable))
    print(f.format('{0:s->capitalize}', variable))
    print(f.format('{0:s->title}', variable))
    print(f.format('{0:s->lowercase->replace("hello ", "Goodbye ")->lowercase}', variable))
    print(f.format('{0:s->substring(6, -1)}', variable))
    print(f.format('{0:.2}', variable))