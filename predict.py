# Prediction interface for Cog ⚙️
# https://cog.run/python

from cog import BasePredictor, Input

class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load the model into memory to make running multiple predictions efficient"""
        print("Setting up...")
        # No setup needed for this simple predictor
        pass

    def predict(
        self,
        text: str = Input(description="Text to append to 'hello world '")
    ) -> str:
        """Returns 'hello world ' concatenated with the input text"""
        print(f"Received input: {text}")
        output = f"hello world {text}"
        print(f"Returning output: {output}")
        return output
