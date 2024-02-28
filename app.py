from presidio_analyzer import AnalyzerEngine, EntityRecognizer, LocalRecognizer, Pattern, PatternRecognizer, RecognizerRegistry, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts, NlpEngineProvider, TransformersNlpEngine
from presidio_analyzer.predefined_recognizers import EmailRecognizer, PhoneRecognizer, SpacyRecognizer
from presidio_anonymizer import AnonymizerEngine, OperatorConfig
from typing import List, Optional
# Create nlp engine 

# Configuration avec spacy uniquement 
# configuration = {
#     "nlp_engine_name": "spacy",
#     "models": [{"lang_code":"fr", "model_name": "fr_core_news_sm"}],
#     "ner_model_configuration":
#         {
#         "model_to_presidio_entity_mapping":
#             {
#             "LOC": "LOCATION",
#             "PER": "PERSON"
            
#             }

#     }
# }

# Configuration avec transformers

configuration = {
     "nlp_engine_name": "transformers",
     "models": [{
        "lang_code":"fr",
        "model_name":
        {
            "spacy": "fr_core_news_sm",
            "transformers": "Jean-Baptiste/camembert-ner-with-dates"
        }
                }],
     "ner_model_configuration":
         {
         "model_to_presidio_entity_mapping":
             {
             "LOC": "LOCATION",
             "PER": "PERSON"
           
             }
     }
 }

# with spacy only 
provider = NlpEngineProvider(nlp_configuration=configuration)




# Test d'un custom Recognizer basé sur le nom, prenom etc .. 
class PersonalDataRecognizer(EntityRecognizer):

    def __init__(self, supported_entities: List[str], data:dict,  name: str = None, supported_language: str = "en", version: str = "0.0.1", context: Optional[List[str]] = None):
        super().__init__(supported_entities, name, supported_language, version, context)

        self.first_name = data.get("first_name", "").upper()
        self.last_name = data.get("last_name", "").upper()

    def analyze(self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts) -> List[RecognizerResult]:
        print("yoo")

        results = []
        for token in nlp_artifacts.tokens:
            # print(token.ent_type_)
            if token.text.upper() in [self.first_name, self.last_name]:
                result = RecognizerResult(
                    entity_type="USER_NAME", 
                    start = token.idx, 
                    end = token.idx + len(token), 
                    score = 1
                )
                results.append(result)                
        
        return results

    
# Create several recognizer 
registry = RecognizerRegistry()
email = EmailRecognizer(supported_language="fr")
phone = PhoneRecognizer(supported_language="fr")
personal = PersonalDataRecognizer("PERS", {"first_name": "sacha", "last_name": "schutz"} , supported_language="fr")
spacy = SpacyRecognizer(supported_language="fr",supported_entities=["PERSON", "LOCATION", "DATE"])


registry.add_recognizer(email)
registry.add_recognizer(phone)
registry.add_recognizer(personal)
registry.add_recognizer(spacy)

# registry.add_recognizer(personal)

# Create analyzer 

# text = "Je suis Sacha Schutz et mon email est sacha@labsquare.org. et mon tel est le 0654545465. J'habite à Caen"

text = """
Je m'appelle Boby Lapointe et j'habite à Paris. Mon téléphone est le +33545464355. Je suis née le 3 mai 1924
à Aix-La-Chapelle

"""

analyzer = AnalyzerEngine(nlp_engine=provider.create_engine(), registry=registry)
analyzer_results = analyzer.analyze(text=text, language="fr")

# Anonymize 
engine = AnonymizerEngine()

operators = {
    "DEFAULT" : OperatorConfig("replace")
}
result = engine.anonymize(text=text, analyzer_results=analyzer_results, operators=operators)


print(analyzer.get_supported_entities("fr"))
print(result.text)
