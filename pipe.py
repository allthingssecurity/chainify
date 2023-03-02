from abc import ABC, abstractmethod
import openai
import requests

class Model(ABC):
    @abstractmethod
    def execute(self, input_text):
        pass

class Prompt(ABC):
    def __init__(self, input_text, model, output_text):
        self.input_text = input_text
        self.model = model
        self.output_text = output_text
    
    @abstractmethod
    def execute(self):
        pass

class Filter(ABC):
    def __init__(self, input_text):
        self.input_text = input_text
    
    @abstractmethod
    def execute(self):
        pass

class RestApiModel(Model):
    def __init__(self, url):
        self.url = url
    
    def execute(self, input_text):
        payload = {"input_text": input_text}
        response = requests.post(self.url, json=payload)
        output_text = response.json()["output_text"]
        return output_text

class OpenAIModel(Model):
    def __init__(self, api_key, engine):
        self.api_key = api_key
        self.engine = engine
    
    def execute(self, input_text):
        openai.api_key = self.api_key
        response = openai.Completion.create(
            engine=self.engine,
            prompt=input_text,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )
        output_text = response.choices[0].text
        #print(output_text)
        return output_text
class RestApiPrompt(Prompt):
    def execute(self):
        output = self.model.execute(self.input_text)
        return output

class OpenAIPrompt(Prompt):
    def __init__(self, input_text, model, output_text):
        super().__init__(input_text, model, output_text)
        #self.engine = engine
    
    def execute(self):
        output_text = self.model.execute(self.input_text)
        return output_text
        
class CapitalizeFilter(Filter):
    def execute(self,input_text):
        print("entered filter")
        print(input_text)
        output_text = input_text.capitalize().strip()
        print("output string=***",output_text)
        return output_text

class PipelineStep:
    def __init__(self, component):
        self.component = component
    
    def execute(self, input_text):
        output_text = self.component.execute()
        return output_text

class Pipeline:
    def __init__(self, steps):
        self.steps = steps
    
    def execute(self, input_text):
        for step in self.steps:
            if isinstance(step.component, Prompt):
                output_text = step.component.execute()
            elif isinstance(step.component, Filter):
                output_text = step.component.execute(input_text)
            else:
                raise ValueError("Invalid pipeline step: {}".format(step))
            input_text = output_text
        return input_text

# Initialize models
restapi_model = RestApiModel("http://localhost:5000/model")
openai_model = OpenAIModel("", "text-davinci-003")

# Initialize prompts and filters
restapi_prompt = RestApiPrompt("Hello, world!", restapi_model, "Output text")
openai_prompt = OpenAIPrompt("Write a python program for fibonnaci series", openai_model, "Output text")
capitalize_filter = CapitalizeFilter("")

# Initialize pipeline
pipeline = Pipeline([
    PipelineStep(openai_prompt),
    PipelineStep(capitalize_filter)
])

# Execute pipeline
output_text = pipeline.execute("")
print(output_text)
