import os
import json
import logging
import psycopg2
from app.db.db import get_db_connection
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample Ayurvedic Data Seed
SAMPLE_DATA = [
    {
        "condition_name": "Amlapitta",
        "category": "Digestive Disorder",
        "symptoms": ["burning sensation in stomach", "sour eructation", "heartburn", "nausea"],
        "causes": ["excessive spicy food", "irregular meals", "stress", "alcohol"],
        "dosha": ["Pitta"],
        "samprapti": "Increased Pitta causes acidity and irritation in the stomach lining.",
        "treatment_principles": ["Pitta Shodhana", "Deepana", "Pachana"],
        "diet": ["Pomegranates", "Milk with Ghee", "Barley", "Green gram"],
        "lifestyle": ["Avoid afternoon naps", "Meditation", "Cool environment"],
        "herbs": ["Amalaki", "Guduchi", "Shatavari"],
        "formulations": ["Avipattikara Churna", "Kamadugha Rasa", "Sutashekhar Rasa"],
        "search_text": "Acidity, burning stomach, heartburn, acid reflux, pitta imbalance, sour burps",
        "ai_content": {
            "rupa_symptoms": ["Burning in throat", "Upper abdominal pain", "Nausea"],
            "nidana_causes": ["Pitta-aggravating foods", "Suppression of natural urges"],
            "dosha_involvement": "Pitta (Pachaka Pitta)",
            "treatment_principles": ["Cooling agents", "Ghee preparation"],
            "diet": ["Sweet fruits", "Coconut water"],
            "lifestyle": ["Regular sleep", "Yogic breathing"]
        }
    },
    {
        "condition_name": "Jwara",
        "category": "Fever",
        "symptoms": ["high body temperature", "body pain", "heaviness in head", "loss of appetite"],
        "causes": ["seasonal change", "improper digestion", "immunosuppression"],
        "dosha": ["Vata-Pitta-Kapha"],
        "samprapti": "Obstruction of channels by Ama leading to body heat.",
        "treatment_principles": ["Langhana", "Pachana", "Swedana"],
        "diet": ["Warm fluids", "Light boiled rice", "Ginger water"],
        "lifestyle": ["Complete bed rest", "Avoid cold exposure"],
        "herbs": ["Tulsi", "Guduchi", "Musta", "Kiratatikta"],
        "formulations": ["Mahasudarshan Churna", "Laxmi Vilas Ras", "Amritarishta"],
        "search_text": "Fever, body ache, headache, temperature, flu symptoms, ayurvedic fever management",
        "ai_content": {
            "rupa_symptoms": ["Fever", "Anorexia", "Thirst"],
            "nidana_causes": ["Physical exertion", "Mental stress"],
            "dosha_involvement": "Vata-Pitta primary",
            "treatment_principles": ["Ama detoxification", "Rest"],
            "diet": ["Muda-yusha (Moong soup)", "Peyadi krama"],
            "lifestyle": ["Adequate rest", "Meditation"]
        }
    },
    {
        "condition_name": "Sandhigata Vata",
        "category": "Joint Disease",
        "symptoms": ["joint pain", "stiffness", "swelling", "crepitus"],
        "causes": ["old age", "excessive travel", "dry food", "injury"],
        "dosha": ["Vata"],
        "samprapti": "Drying up of synovial fluid due to Vata aggravation.",
        "treatment_principles": ["Snehana", "Swedana", "Basti"],
        "diet": ["Warm and oily food", "Garlic", "Fenugreek", "Ginger"],
        "lifestyle": ["Abhyanga (oil massage)", "Warm compresses", "Gentle yoga"],
        "herbs": ["Guggulu", "Ashwagandha", "Shallaki", "Rasna"],
        "formulations": ["Yogaraj Guggulu", "Mahanarayan Oil", "Rasnadi Kwath"],
        "search_text": "Joint pain, osteoarthritis, joint stiffness, knee pain, vata joints, creaking bones",
        "ai_content": {
            "rupa_symptoms": ["Pain on movement", "Stiffness in the morning"],
            "nidana_causes": ["Aging", "Vata aggravating diet"],
            "dosha_involvement": "Vata (Vyana Vayu)",
            "treatment_principles": ["Oleation", "External heat"],
            "diet": ["Sesame seeds", "Ghee"],
            "lifestyle": ["Daily oil massage", "Avoid cold wind"]
        }
    },
    {
        "condition_name": "Manas Roga (Chinta/Anxiety)",
        "category": "Psychological Disorder",
        "symptoms": ["anxiety", "restlessness", "racing thoughts", "insomnia", "palpitations"],
        "causes": ["stress", "poor sleep", "excessive mental work", "vata aggravation"],
        "dosha": ["Vata", "Sadhaka Pitta"],
        "samprapti": "Vitiated Vata affects the Hridaya (heart/mind) and disturbs the Manas (mind).",
        "treatment_principles": ["Shanti Karma", "Medhya Rasayana", "Nasya"],
        "diet": ["Walnuts", "Warm milk", "Almonds", "Sesame seeds"],
        "lifestyle": ["Meditation", "Deep breathing (Pranayama)", "Oil massage (Shirodhara)"],
        "herbs": ["Brahmi", "Shankhapushpi", "Jatamansi"],
        "formulations": ["Brahmi Vati", "Saraswatarishta", "Manasamitra Vatakam"],
        "search_text": "Anxiety, stress, worry, panic, restlessness, mental fatigue, mind racing, vata in mind",
        "ai_content": {
            "rupa_symptoms": ["Anxiety", "Fear", "Irritability"],
            "nidana_causes": ["High stress environments", "Irregular routine"],
            "dosha_involvement": "Vata (Prana Vayu)",
            "treatment_principles": ["Grounding therapies", "Relaxation"],
            "diet": ["Buffalo milk", "Sweet tastes"],
            "lifestyle": ["Abhyanga", "Consistent sleep schedule"]
        }
    },
    {
        "condition_name": "Pandu / Klama (Fatigue)",
        "category": "General Weakness",
        "symptoms": ["fatigue", "weakness", "lethargy", "pale skin", "shortness of breath"],
        "causes": ["nutritional deficiency", "over-exertion", "poor digestion"],
        "dosha": ["Pitta", "Vata"],
        "samprapti": "Impairment of Rasa Dhatu leading to lack of energy and vitality.",
        "treatment_principles": ["Deepana", "Pachana", "Rakta Vardhaka"],
        "diet": ["Pomegranate", "Spinach", "Dates", "Iron-rich foods"],
        "lifestyle": ["Moderate exercise", "Pranayama", "Sun exposure"],
        "herbs": ["Amalaki", "Punarnava", "Loha Bhasma"],
        "formulations": ["Dhatri Lauha", "Punarnavasava", "Lohasava"],
        "search_text": "Fatigue, weakness, tiredness, anemic, low energy, lethargy, physical exhaustion",
        "ai_content": {
            "rupa_symptoms": ["General debility", "Malaise", "Pallor"],
            "nidana_causes": ["Malnutrition", "Blood loss"],
            "dosha_involvement": "Ranjaka Pitta / Rasa Dhatu Kshaya",
            "treatment_principles": ["Nutritional support", "Digestive firing"],
            "diet": ["Amla juice", "Beetroot"],
            "lifestyle": ["Sufficient rest", "Gentle yoga"]
        }
    }
]

def seed_database():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # 1. Ensure table exists using schema.sql logic
            logger.info("Initializing database schema...")
            with open('app/db/schema.sql', 'r') as f:
                cur.execute(f.read())
            
            # 2. Seed data
            logger.info("Seeding data...")
            for data in SAMPLE_DATA:
                cur.execute("""
                    INSERT INTO conditions (
                        condition_name, category, symptoms, causes, dosha, 
                        samprapti, diagnosis_logic, treatment_principles, 
                        diet, lifestyle, herbs, formulations, search_text, ai_content
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (condition_name) DO UPDATE SET
                        ai_content = EXCLUDED.ai_content,
                        search_text = EXCLUDED.search_text,
                        herbs = EXCLUDED.herbs,
                        formulations = EXCLUDED.formulations
                """, (
                    data["condition_name"], data["category"], data["symptoms"], 
                    data["causes"], data["dosha"], data["samprapti"], 
                    "", data["treatment_principles"], data["diet"], 
                    data["lifestyle"], data["herbs"], data["formulations"],
                    data["search_text"], json.dumps(data["ai_content"])
                ))
            
            conn.commit()
            logger.info("Database successfully seeded with Ayurvedic conditions.")
            
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    seed_database()
