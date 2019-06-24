from pygments.lexer import RegexLexer, bygroups, using, this, words
from pygments.token import Text, Keyword, Name, String, Number, Operator, Punctuation, Comment

__all__ = ['ShaderLexer']

class ShaderLexer(RegexLexer):
    name      = 'Shader'
    aliases   = ['shader']
    filenames = ['*.shader']
    mimetypes = ['text/x-shader']

    _ws = r'\s*(?:/[*].*?[*]/\s*)?'

    tokens = {
        'root': [
            ('^#if\s+0', Comment.Preproc, 'if0'),
            ('^#', Comment.Preproc, 'macro'),
            ('^(' + _ws + r')(#if\s+0)',
             bygroups(using(this), Comment.Preproc), 'if0'),
            ('^(' + _ws + ')(#)',
             bygroups(using(this), Comment.Preproc), 'macro'),
            (r'\n', Text),
            (r'\s+', Text),
            (r'\\\n', Text),
            (r'//(\n|[\w\W]*?[^\\]\n)', Comment.Single),
            (r'/(\\\n)?[*][\w\W]*?[*](\\\n)?/', Comment.Multiline),
            (r'/(\\\n)?[*][\w\W]*', Comment.Multiline),
            (r'(2|3)D\b', Keyword),
            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+[LlUu]*', Number.Float),
            (r'(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Number.Float),
            (r'0x[0-9a-fA-F]+[LlUu]*', Number.Hex),
            (r'0[0-7]+[LlUu]*', Number.Oct),
            (r'\d+[LlUu]*', Number.Integer),
            (r'[~!%^&*+=|?:<>/-]', Operator),
            (r'[;{}()\[\],.]', Punctuation),
            (r'(L?)(")', bygroups(String.Affix, String), 'string'),
            (r"(L?)(')(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])(')", bygroups(String.Affix, String.Char, String.Char, String.Char)),
            (words((
                # ShaderLab
                'Shader', 'Properties', 'SubShader', 'Pass', 'UsePass', 'GrabPass', 'Tags',
                'Range', 'Float', 'Int', 'Color', 'Vector', '2D', 'Cube', '3D',
                'Cull', 'ZTest', 'ZWrite', 'Offset', 'Blend', 'BlendOp', 'AlphaToMask', 'ColorMask',
                'Stencil', 'Ref', 'ReadMask', 'WriteMask', 'Comp', 'CompFront', 'CompBack', 'PassFront', 'PassBack', 'Fail', 'FailFront', 'FailBack', 'ZFail', 'ZFailFront', 'ZFailBack',
                'Name',
                'Material', 'Lighting', 'SeparateSpecular', 'ColorMaterial', 'Diffuse', 'Ambient', 'Specular', 'Shininess', 'Emission',
                'SetTexture', 'combine', 'constantColor',
                'AlphaTest',
                'Fog', 'Mode', 'Density', 'Range',
                'BindChannels', 'Bind',
                'LOD',
                'Fallback', 'CustomEditor', 'Category',
                'CGPROGRAM', 'CGINCLUDE', 'ENDCG',

                # Cg
                'asm', 'asm_fragment', 'auto',
                'break',
                'case', 'catch', 'class', 'column_major', 'compile', 'const', 'const_cast', 'continue',
                'decl', 'default', 'delete', 'discard', 'do', 'dword', 'dynamic_cast',
                'else', 'emit', 'enum', 'explicit', 'extern',
                'for', 'friend',
                'get', 'goto',
                'if', 'in', 'inline', 'inout', 'interface',
                'matrix', 'mutable',
                'namespace', 'new',
                'operator', 'out',
                'packed', 'pass', 'pixelfragment', 'pixelshader', 'private', 'protected', 'public',
                'register', 'reinterpret_cast', 'return', 'row_major',
                'sampler_state', 'shared', 'sizeof', 'static', 'static_cast', 'string', 'struct', 'switch',
                'technique', 'template', 'texture', 'texture1D', 'texture2D', 'texture3D', 'textureCUBE', 'textureRECT', 'this', 'throw', 'try', 'typedef', 'typeid', 'typename',
                'uniform', 'union', 'using',
                'vector', 'vertexfragment', 'vertexshader', 'virtual', 'volatile',
                'while'),
                   suffix=r'\b'), Keyword),
            (words((
                'TRUE', 'true', 'FALSE', 'false', 'NULL',

                # Semantics
                'BINORMAL', 'BLENDINDICES', 'BLENDWEIGHT',
                'CENTROID', 'CLPV', 'CONTROLPOINT_ID', 'COL', 'COLOR',
                'DEPR', 'DEPTH', 'DIFFUSE',
                'EDGETESS',
                'FACE', 'FLAT', 'FOG', 'FOGC', 'FOGCOORD', 'FOGP',
                'HPOS',
                'INNERTESS', 'INSTANCEID',
                'NOPERSPECTIVE', 'NORMAL',
                'PATCH', 'POSITION', 'PRIMITIVEID', 'PSIZ', 'PSIZE',
                'SPECULAR', 'SV_Depth', 'SV_POSITION', 'SV_Target', 'SV_VertexID',
                'TANGENT', 'TESSCOORD', 'TESSFACTOR',
                'UV',
                'VERTEXID', 'VFACE', 'VPOS'),
                   suffix=r'\b'), Keyword.Constant),
            (r'(ATTR|BCOL|C|CLP|COL|COLOR|SV_Target|TEX|TEXCOORD|TEXUNIT)[0-9]+\b', Keyword.Constant),
            (r'(void|signed|unsigned|cint|cfloat|char|short|long|double|((bool|fixed|float|half|int)(([1234](x[1234])?)?)?)|(sampler((1D|2D)(ARRAY)?|3D|RECT|CUBE)?(_half|_float)?))\b', Keyword.Type),
            (words((
                # Mathematical
                'abs', 'acos', 'all', 'any', 'asin', 'atan', 'atan2',
                'ceil', 'clamp', 'clip', 'cos', 'cosh', 'cross',
                'degress', 'determinant', 'dot',
                'exp', 'exp2',
                'floor', 'fmod', 'frac', 'frexp', 'fwidth',
                'isfinite', 'isinf', 'isnan',
                'ldexp', 'lerp', 'lit', 'log', 'log2', 'log10',
                'max', 'min', 'modf', 'mul',
                'noise',
                'pow',
                'radians', 'round', 'rsqrt',
                'saturate', 'sign', 'sin', 'sincos', 'sinh', 'smoothstep', 'step', 'sqrt',
                'tan', 'tanh', 'transpose', 'trunc',

                # Geometric
                'distance', 'faceforward', 'length', 'normalize', 'reflect', 'refract',

                # Texture Map
                'tex1D', 'tex1Dproj', 'tex2D', 'tex2Dproj', 'tex3D', 'tex3Dproj',
                'texRECT', 'texRECTproj', 'texCUBE', 'texCUBEproj',

                # Derivative
                'ddx', 'ddy',

                # Debugging
                'debug'),
                   suffix=r'\b'), Keyword.Builtin),
            ('[a-zA-Z_]\w*', Name),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|'
             r'u[a-fA-F0-9]{4}|U[a-fA-F0-9]{8}|[0-7]{1,3})', String.Escape),
            (r'[^\\"\n]+', String),
            (r'\\\n', String),
            (r'\\', String),
        ],
        'macro': [
            (r'(include)(' + _ws + r')([^\n]+)', bygroups(Comment.Preproc, Text, Comment.PreprocFile)),
            (r'[^/\n]+', Comment.Preproc),
            (r'/[*](.|\n)*?[*]/', Comment.Multiline),
            (r'//.*?\n', Comment.Single, '#pop'),
            (r'/', Comment.Preproc),
            (r'(?<=\\)\n', Comment.Preproc),
            (r'\n', Comment.Preproc, '#pop'),
        ],
        'if0': [
            (r'^\s*#if.*?(?<!\\)\n', Comment.Preproc, '#push'),
            (r'^\s*#el(?:se|if).*\n', Comment.Preproc, '#pop'),
            (r'^\s*#endif.*?(?<!\\)\n', Comment.Preproc, '#pop'),
            (r'.*?\n', Comment),
        ],
    }
