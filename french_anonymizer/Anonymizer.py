
from presidio_analyzer import AnalyzerEngine, EntityRecognizer, LocalRecognizer, Pattern, PatternRecognizer, RecognizerRegistry, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts, NlpEngineProvider, TransformersNlpEngine
from presidio_analyzer.predefined_recognizers import EmailRecognizer, PhoneRecognizer, SpacyRecognizer
from presidio_anonymizer import AnonymizerEngine, OperatorConfig
from typing import List, Optional

SPACY_CONFIGURATION = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code":"fr", "model_name": "fr_core_news_sm"}],
    "ner_model_configuration":
        {
        "model_to_presidio_entity_mapping":
            {
            "LOC": "LOCATION",
            "PER": "PERSON"
            }
    }
}

TRANSFORMER_CONFIGURATION= {
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
             "PER": "PERSON",
             "ORG": "ORGANIZATION"       
             }
     }
 }

class Anonymizer:


    def __init__(self, nlp_engine_name:str = "spacy"):

        self.provider = self._create_provider(nlp_engine_name)
        self.registry = self._create_registry() 
        self.analyzer = AnalyzerEngine(nlp_engine = self.provider.create_engine(), registry = self.registry)
        self.anonymizer = AnonymizerEngine()
        self.anonymizer_operators = {
            "DEFAULT" : OperatorConfig("replace")
        }


    def _create_provider(self, nlp_engine_name:str = "spacy") -> NlpEngineProvider:

        if nlp_engine_name not in ("spacy", "transformer"):
            raise Exception(f"Unknown nlp engine name {nlp_engine_name}")

        if nlp_engine_name == "spacy":
            provider = NlpEngineProvider(nlp_configuration = SPACY_CONFIGURATION)
        if nlp_engine_name == "transformer":
            provider = NlpEngineProvider(nlp_configuration = TRANSFORMER_CONFIGURATION)

        return provider

    def _create_pattern(self, entity:str, regex :str ) -> PatternRecognizer :
        # Define the regex pattern in a Presidio `Pattern` object:
        pattern = Pattern(name=entity, regex=regex, score=0.5)

        # Define the recognizer with one or more patterns
        recognizer = PatternRecognizer(supported_entity=entity, patterns=[pattern], supported_language="fr")

        return recognizer 

    def _create_registry(self) -> RecognizerRegistry:

        registry = RecognizerRegistry()
        email = EmailRecognizer(supported_language="fr")
        phone = PhoneRecognizer(supported_language="fr")
        spacy = SpacyRecognizer(supported_language="fr",supported_entities=["PERSON", "LOCATION", "DATE"])
        large_number = self._create_pattern("LARGE_NUMBER", r"\d{5,}")
        registry.add_recognizer(email)
        registry.add_recognizer(phone)
        registry.add_recognizer(spacy)
        registry.add_recognizer(large_number)
        return registry

    def from_text(self, text:str) -> str:

        result = self.analyzer.analyze(text=text, language = "fr")
        result = self.anonymizer.anonymize(text=text, analyzer_results=result, operators=self.anonymizer_operators )
        return result.text


    




    
if __name__ == "__main__":

    print("Chargement des modèles ...")
    i = Anonymizer("transformer")
    while True:
        text = input("Votre texte à anonymiser: ")
 
        res = i.from_text(text)

        print(res)


