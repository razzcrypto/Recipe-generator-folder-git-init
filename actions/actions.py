from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import spacy
import random

# Load spaCy model
nlp = spacy.load("en_core_web_md")

class ActionGenerateRecipe(Action):
    def name(self) -> Text:
        return "action_generate_recipe"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get dish from slot
        dish = tracker.get_slot("dish")
        if not dish:
            # Try to extract from last user message
            last_message = tracker.latest_message.get("text", "")
            doc = nlp(last_message)
            # Look for noun phrases that might be dishes
            for chunk in doc.noun_chunks:
                if chunk.root.pos_ == "NOUN":
                    dish = chunk.text
                    break
        
        # Get dietary requirements
        dietary_reqs = tracker.get_slot("dietary_requirements") or []
        
        if not dish:
            dispatcher.utter_message(text="I didn't catch what dish you want. Could you please specify?")
            return []
        
        # Generate recipe based on dish and requirements
        recipe = self.generate_recipe(dish, dietary_reqs)
        
        dispatcher.utter_message(text=f"Here's your recipe for {dish}:\n{recipe}")
        return []

    def generate_recipe(self, dish: str, dietary_reqs: List[str]) -> str:
        """Generate a recipe based on the dish and dietary requirements"""
        
        # Base ingredients and steps (in a real app, you'd use a database or API)
        base_ingredients = {
            "pasta": ["pasta", "olive oil", "garlic", "salt"],
            "chicken curry": ["chicken", "curry powder", "coconut milk", "onion"],
            "vegetable soup": ["mixed vegetables", "vegetable stock", "onion", "herbs"],
            "chocolate cake": ["flour", "sugar", "cocoa powder", "eggs", "butter"],
            "beef stew": ["beef", "potatoes", "carrots", "onion", "beef stock"]
        }
        
        # Dietary substitutions
        substitutions = {
            "vegetarian": {
                "chicken": "tofu",
                "beef": "mushrooms",
                "chicken curry": "tofu curry"
            },
            "gluten-free": {
                "flour": "gluten-free flour",
                "pasta": "gluten-free pasta"
            },
            "dairy-free": {
                "butter": "coconut oil",
                "milk": "almond milk"
            }
        }
        
        # Get base recipe
        ingredients = base_ingredients.get(dish.lower(), ["main ingredient", "seasoning", "oil"])
        steps = self.generate_cooking_steps(dish)
        
        # Apply dietary requirements
        for req in dietary_reqs:
            req = req.lower()
            if req in substitutions:
                for original, substitute in substitutions[req].items():
                    ingredients = [substitute if ingredient == original else ingredient for ingredient in ingredients]
                    dish = substitute if dish.lower() == original else dish
        
        # Format the recipe
        recipe = f"**{dish.title()} Recipe**\n\n"
        recipe += "**Ingredients:**\n- " + "\n- ".join(ingredients) + "\n\n"
        recipe += "**Instructions:**\n" + "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
        
        return recipe
    
    def generate_cooking_steps(self, dish: str) -> List[str]:
        """Generate cooking steps based on dish type"""
        dish = dish.lower()
        
        if "pasta" in dish:
            return [
                "Boil water in a large pot",
                "Add salt and pasta, cook according to package instructions",
                "Drain pasta, reserving some cooking water",
                "Mix with sauce and serve"
            ]
        elif "curry" in dish:
            return [
                "Heat oil in a pan and sauté onions until soft",
                "Add main protein and brown slightly",
                "Add curry powder and stir for 1 minute",
                "Add coconut milk and simmer for 20 minutes",
                "Season to taste and serve with rice"
            ]
        elif "soup" in dish:
            return [
                "Sauté onions in a large pot until translucent",
                "Add vegetables and cook for 5 minutes",
                "Pour in stock and bring to a boil",
                "Reduce heat and simmer for 20-30 minutes",
                "Season with salt, pepper, and herbs"
            ]
        elif "cake" in dish:
            return [
                "Preheat oven to 350°F (175°C)",
                "Mix dry ingredients in one bowl",
                "Cream butter and sugar, then add eggs",
                "Combine wet and dry ingredients",
                "Pour into greased pan and bake for 30-35 minutes"
            ]
        elif "stew" in dish:
            return [
                "Brown meat in a large pot",
                "Add chopped vegetables and cook for 5 minutes",
                "Add stock and bring to a boil",
                "Reduce heat, cover and simmer for 2 hours",
                "Season to taste before serving"
            ]
        else:
            return [
                "Prepare all ingredients",
                "Cook the main component",
                "Add seasonings and other ingredients",
                "Cook until done",
                "Serve and enjoy!"
            ]
