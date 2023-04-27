import requests
import openai
import random

# NodeMCU's IP address
nodemcu_ip = "192.168.1.100"

# OpenAI Variables
api_key = "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"
model = "gpt-3.5-turbo" # text-ada-001 text-babbage-001 text-curie-001 gpt-3.5-turbo
temp = 1.0
tokens = 40

# User chosen plant variables
plant_dict = {
    '{plant_type}': '',
    '{plant_name}': '',
    '{owner_name}': '',
    '{living_situation}': '',
    '{tone}': '',
    '{character}': '',
    '{swearing}': ''
}

def remove_quotes(s):
    return s.replace('"', '').replace("'", '')

def replace_placeholders(s):
    global plant_dict, plant_type, plant_name, owner_name, living_situation, tone, character, swearing
    for key, value in plant_dict.items():
        s = s.replace(key, value)
    return s

def update_plant_variables():
    global plant_dict

    with open('plant_variables.txt', 'r') as f:
        # Read new values into a list
        new_values = [remove_quotes(line.strip()) for line in f]
    
    for i, key in enumerate(plant_dict):
        plant_dict[key] = new_values[i]

def get_gpt_instruction():
    gpt_file = open('gpt_instruction.txt')
    gpt_instruction = gpt_file.read()
    return gpt_instruction

def get_gpt_response(prompt):
    # Set up OpenAI API client
    openai.api_key = api_key

    if model == "gpt-3.5-turbo":
        messages = []
        messages.append({"role": "system", "content": prompt})
        # Make a request to the GPT-3.5 Chat API
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = messages,
            max_tokens = tokens,
            n=1,
            temperature = temp
        )
        # Extract and return the generated response
        chat_response = completion.choices[0].message.content
    else:
        completion = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=tokens,
            n=1,
            stop=None,
            temperature=temp,
        )

        chat_response = completion.choices[0].text.strip()
    chat_response
    return chat_response

def remove_extra_newlines(input_str):
    lines = input_str.split('\n')

    new_lines = []
    for i, line in enumerate(lines):
        if ':' in line:
            continue
        if i > 0 and line == '':
            continue
        new_lines.append(line)

    return ' '.join(new_lines)

def cut_string(string):
    last_index = -1
    for char in ['.', '!', '?']:
        index = string.rfind(char)
        if index > last_index:
            last_index = index
    if last_index != -1:
        return string[:last_index+1]
    else:
        return string

def random_uppercase_char():
    excluded_letters = ['Q', 'X', 'Z', 'K', 'V', 'A', 'I']  # exclude the least used letters
    while True:
        letter = chr(random.randint(65, 90))
        if letter not in excluded_letters:
            return letter

def generate_response(plant_status):
    update_plant_variables()
    random_starting_letter = random_uppercase_char()
    gpt_system_instruction = replace_placeholders(get_gpt_instruction()) + plant_status + '\n\"' + random_starting_letter
    #print(gpt_system_instruction)
    gpt_response = random_starting_letter + get_gpt_response(gpt_system_instruction)
    gpt_response = remove_quotes(gpt_response)
    gpt_response = cut_string(gpt_response)
    gpt_response = remove_extra_newlines(gpt_response)
    return gpt_response

def get_plant_status(water_level):
    if(water_level<5):
        return 'extremely underwatered'
    elif(water_level<15):
        return 'underwatered'
    elif (water_level < 80):
        return 'not thirsty,healthy'
    elif (water_level < 90):
        return 'overwatered'
    else:
        return 'extremely overwatered'
    

def get_sensor_percentage():
    url = f"http://{nodemcu_ip}/sensor"
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            sensor_percentage = response.text
            return int(sensor_percentage)

        else:
            print(f"Error: {response.status_code}")
            return -1
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        return -1

if __name__ == '__main__':
    while True:
        print()
        user_input = input() # Wait for user input

        if user_input == 'exit':
            break # Exit the loop if the user enters 'exit'
        
        water_sensor_percentage = get_sensor_percentage()

        print(water_sensor_percentage, '%')
        plant_status = get_plant_status(water_sensor_percentage)
        print(plant_status)

        print(generate_response(plant_status))