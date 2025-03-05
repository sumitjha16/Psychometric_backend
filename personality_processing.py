import os
from mistralai import Mistral  # Correct import

class PersonalityAssessment:
    def __init__(self, api_key):
        self.client = Mistral(api_key=api_key)
        self.personality_traits = {
            '1': {'A': {'primary': 'Leader', 'subtrait': 'Fearless Finisher'},
                  'B': {'primary': 'Strategist', 'subtrait': 'Smart Planner'},
                  'C': {'primary': 'Empath', 'subtrait': 'Motivator Extraordinaire'},
                  'D': {'primary': 'Adventurer', 'subtrait': 'Risk-Taker Extraordinaire'}},
            '2': {'A': {'primary': 'Adventurer', 'subtrait': 'Free Spirit'},
                  'B': {'primary': 'Strategist', 'subtrait': 'Practical Planner'},
                  'C': {'primary': 'Empath', 'subtrait': 'Heartfelt Negotiator'},
                  'D': {'primary': 'Leader', 'subtrait': 'Visionary Trailblazer'}},
            '3': {'A': {'primary': 'Adventurer', 'subtrait': 'Thrill-Seeker'},
                  'B': {'primary': 'Strategist', 'subtrait': 'Master Planner'},
                  'C': {'primary': 'Empath', 'subtrait': 'Supportive Soul'},
                  'D': {'primary': 'Leader', 'subtrait': 'The Boss of Fun'}},
            '4': {'A': {'primary': 'Leader', 'subtrait': 'Visionary Change-Maker'},
                  'B': {'primary': 'Strategist', 'subtrait': 'Practical Impact-Maker'},
                  'C': {'primary': 'Empath', 'subtrait': 'The People\'s Champion'},
                  'D': {'primary': 'Adventurer', 'subtrait': 'The Innovator'}},
            '5': {'A': {'primary': 'Leader', 'subtrait': 'Ethical Boss'},
                  'B': {'primary': 'Empath', 'subtrait': 'Ride-or-Die Friend'},
                  'C': {'primary': 'Strategist', 'subtrait': 'Clever Fixer'},
                  'D': {'primary': 'Adventurer', 'subtrait': 'Carefree Rebel'}},
            '6': {'A': {'primary': 'Leader', 'subtrait': 'The Unstoppable'},
                  'B': {'primary': 'Strategist', 'subtrait': 'The Game Changer'},
                  'C': {'primary': 'Empath', 'subtrait': 'The Emotional Anchor'},
                  'D': {'primary': 'Adventurer', 'subtrait': 'The Rule-Breaker'}}
        }

    def process_personality(self, selected_options):
        if len(selected_options) != 6:
            raise ValueError("Exactly 6 options must be provided.")

        selected_traits = [
            self.personality_traits[str(i+1)][opt]
            for i, opt in enumerate(selected_options)
        ]

        trait_counts = {}
        for trait in selected_traits:
            primary = trait['primary']
            trait_counts[primary] = trait_counts.get(primary, 0) + 1

        dominant_trait = max(trait_counts, key=trait_counts.get)

        prompt = f"""
        Analyze personality profile:
        Dominant Trait: {dominant_trait}
        Detailed Traits: {selected_traits}

        Generate a concise two-paragraph analysis directly addressing the person:
        - First paragraph about their personality in a conversational, intimate tone
        - Second paragraph about career paths, speaking directly to them

        Avoid headings, subheadings. Write as if you're speaking to them personally.
        """

        response = self.client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content


def process_personality_assessment(options, api_key):
    try:
        assessment = PersonalityAssessment(api_key)
        return assessment.process_personality(options)
    except Exception as e:
        print(f"Error processing personality assessment: {e}")
        return f"Error processing personality assessment: {str(e)}"


if __name__ == "__main__":
    api_key = os.getenv("MISTRAL_API_KEY", "your_default_key_here")  # Use env variable
    sample_options = ['A', 'B', 'C', 'D', 'A', 'B']
    result = process_personality_assessment(sample_options, api_key)
    print(result)
