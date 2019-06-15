from .atlas_client_builder import AtlasClientBuilder
from .atlas_request import AtlasRequest, _Lex, _Dep


def lex(x: _Lex):
    x.lemma()
    x.base()
    x.pos()
    x.abbreviations(lambda x: x.lemma())
    x.flexions(lambda x: x.lemma())
    x.hyperonyms(lambda x: x.lemma())
    x.meronyms(lambda x: x.lemma())
    x.parts(lambda x: x.lemma())
    x.causations(lambda x: x.lemma())
    x.collocations(lambda x: x.lemma())
    x.labels()
    x.synonyms(lambda x: x.lemma())


def dep(x: _Dep):
    x.source()
    x.target()
    x.sourceBase()
    x.targetBase()
    x.sourceIndex()
    x.targetIndex()
    x.sourcePos()
    x.targetPos()
    x.sourceTag()
    x.targetTag()
    x.relation()
    x.rawRelation()


request = AtlasRequest.create("text", False).raw().txt().cls().lex(lex).dep(dep)

client = AtlasClientBuilder.http("{url}").with_apikey("{apikey}").with_secret("{secret}").build()

response = client.execute(request)
print(response.json)
