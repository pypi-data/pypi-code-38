from argschema.schemas import DefaultSchema
from argschema import ArgSchema
from argschema.fields import (
        InputDir, InputFile, Float,
        Int, OutputFile, Str, Boolean)

# duplicates so that GenerateEMTileSpecsModule looks identical to
# render-modules version


class RenderClientParameters(DefaultSchema):
    host = Str(
        required=True, description='render host')
    port = Int(
        required=True, description='render post integer')
    owner = Str(
        required=True, description='render default owner')
    project = Str(
        required=True, description='render default project')
    client_scripts = Str(
        required=True, description='path to render client scripts')
    memGB = Str(
        required=False,
        default='5G',
        description='string describing java heap memory (default 5G)')
    validate_client = Boolean(
        required=False,
        default=False,
        description="will avoid problems on windows if we use use_rest")


class RenderParameters(argschema.ArgSchema):
    render = argschema.fields.Nested(
        RenderClientParameters,
        required=True,
        description="parameters to connect to render server")


class OverridableParameterSchema(argschema.schemas.DefaultSchema):
    @pre_load
    def override_input(self, data):
        return self._override_input(data)

    def _override_input(self, data):
        pass

    @staticmethod
    def fix_badkey(data, badkey, goodkey):
        if badkey in data:
            warnings.warn(
                "{b} variable has been deprecated. Will try to fill in "
                "{g} if empty.".format(b=badkey, g=goodkey),
                DeprecationWarning)
            data[goodkey] = (
                data[goodkey] if (goodkey in data) else data[badkey])


class ProcessPoolParameters(argschema.schemas.DefaultSchema):
    pool_size = argschema.fields.Int(required=False, default=1)


class ZValueParameters(  # argschema.schemas.DefaultSchema,
                       OverridableParameterSchema):
    """template schema which interprets z values on which to act
    assumes a hierarchy such that minZ, maxZ are
    superceded by z which is superceded by zValues.
    """
    minZ = argschema.fields.Int(required=False)
    maxZ = argschema.fields.Int(required=False)
    z = argschema.fields.Int(required=False)
    zValues = argschema.fields.List(
            argschema.fields.Int,
            cli_as_single_argument=True,
            required=False)

    @post_load
    def generate_zValues(self, data):
        return self._generate_zValues(data)

    def _generate_zValues(self, data):
        if 'zValues' in data:
            return
        elif 'z' in data:
            data['zValues'] = [data['z']]
        elif ('minZ' in data) and ('maxZ' in data):
            data['zValues'] = range(data['minZ'], data['maxZ'] + 1)
        else:
            raise ValidationError("no z values specified")

    def _override_input(self, data):
        super(ZValueParameters, self)._override_input(data)
        # DEPRECATED
        # the following overrides should be removed in future versions
        self.fix_badkey(data, 'z_index', 'z')
        self.fix_badkey(data, 'zstart', 'minZ')
        self.fix_badkey(data, 'zend', 'maxZ')
        self.fix_badkey(data, 'zs', 'zValues')


class OutputStackParameters(RenderParameters, ZValueParameters,
                            ProcessPoolParameters, OverridableParameterSchema):
    """template schema for writing tilespecs to an output stack"""
    output_stack = argschema.fields.Str(required=True)
    close_stack = argschema.fields.Boolean(required=False, default=False)
    overwrite_zlayer = argschema.fields.Boolean(required=False, default=False)
    output_stackVersion = argschema.fields.Nested(
        RenderStackVersion, required=False)

    def _override_input(self, data):
        super(OutputStackParameters, self)._override_input(data)
        # DEPRECATED
        # the following overrides should be removed in future versions
        self.fix_badkey(data, 'stack', 'output_stack')
        self.fix_badkey(data, 'outputStack', 'output_stack')
