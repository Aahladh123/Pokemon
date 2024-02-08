from flask import Flask, render_template, request, jsonify
import pymysql

app = Flask(__name__)

DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = 'marutiaugust16@gmail.com'
DB_NAME = 'my_database'


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )


def get_pokemon_stats(name_or_number, cursor):
    try:
        if name_or_number.lower() == 'all':
            query = "SELECT * FROM pokemon_values;"
            cursor.execute(query)
        else:
            try:
                query = "SELECT * FROM pokemon_values WHERE Ndex = %s OR UPPER(Pokemon) = UPPER(%s);"
                cursor.execute(query, (name_or_number, name_or_number))
            except:
                # If conversion to integer fails, assume it's a name
                query = "SELECT * FROM pokemon_values WHERE UPPER(Pokemon) = UPPER(%s);"
                cursor.execute(query, (name_or_number.lstrip('#').lstrip('0'), name_or_number))

        results = cursor.fetchall()

        json_results = []
        for result in results:
            json_result = {
                "Ndex": result["Ndex"],
                "Pokemon": result["Pokemon"],
                "Type1": result["Type1"],
                "Type2": result["Type2"],
                "NORMAL": result["NORMAL"],
                "FIRE": result["FIRE"],
                "WATER": result["WATER"],
                "ELECTRIC": result["ELECTRIC"],
                "GRASS": result["GRASS"],
                "ICE": result["ICE"],
                "FIGHTING": result["FIGHTING"],
                "POISON": result["POISON"],
                "GROUND": result["GROUND"],
                "FLYING": result["FLYING"],
                "PSYCHIC": result["PSYCHIC"],
                "BUG": result["BUG"],
                "ROCK": result["ROCK"],
                "GHOST": result["GHOST"],
                "DRAGON": result["DRAGON"],
                "DARK": result["DARK"],
                "STEEL": result["STEEL"],
                "FAIRY": result["FAIRY"]
            }
            weaknesses = ""
            strengths = ""
            neutrals = ""
            nulls = ""

            for i in range(4, len(cursor.description)):
                type_name = cursor.description[i][0]

                try:
                    type_effectiveness = float(result[type_name])
                except ValueError:
                    type_effectiveness = 0

                if type_effectiveness == 0:
                    if type_name != "Type2":
                        nulls += type_name + ", "
                elif type_effectiveness > 1:
                    weaknesses += type_name + ", "
                elif type_effectiveness < 1:
                    strengths += type_name + ", "
                else:
                    neutrals += type_name + ", "

            weaknesses = weaknesses[:-2]
            strengths = strengths[:-2]
            neutrals = neutrals[:-2]
            nulls = nulls[:-2]

            json_result["Weaknesses"] = weaknesses
            json_result["Strengths"] = strengths
            json_result["Neutrals"] = neutrals
            json_result["Nulls"] = nulls

            json_results.append(json_result)

        return json_results

    except Exception as e:
        # Handle exceptions, log errors, or raise them if necessary
        print(f"Error: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    selectedPokemon = None
    selectedType2 = None
    selectedType1 = None

    with get_connection() as connection, connection.cursor() as cursor:
        if request.method == 'POST':
            pokemon_value = request.form['search_term']
            selectedType2 = request.form.get('type2_button')
            selectedType1 = request.form.get('type1_button')

            print(f"Debug: pokemon_value={pokemon_value}, selectedType1={selectedType1}, selectedType2={selectedType2}")

            # If the input is a number, pad with leading zeros
            if pokemon_value.isdigit():
                pokemon_value = f"#{int(pokemon_value):04d}"

            # Logic for setting Type1 and Type2 based on user selection order
            if selectedType2:
                if selectedType1 == selectedType2:
                    # If Type1 and Type2 are the same, set Type2 to None
                    selectedType2 = None
                else:
                    # Swap Type1 and Type2
                    selectedType1, selectedType2 = selectedType2, selectedType1

            print(f"Debug: updated selectedType1={selectedType1}, selectedType2={selectedType2}")

            pokemon_data = get_pokemon_stats(pokemon_value, cursor)

            # Set selectedPokemon if a specific Pokemon is queried
            if pokemon_data and len(pokemon_data) == 1:
                selectedPokemon = pokemon_data[0]

        else:
            default_pokemon = 'All'
            pokemon_data = get_pokemon_stats(default_pokemon, cursor)

    # Print values for debugging if either selectedType1 or selectedType2 is not None
    if selectedType1 is not None or selectedType2 is not None:
        print(f"Debug: Final selectedType1={selectedType1}, selectedType2={selectedType2}")

    # Render the template with the modified data
    return render_template('index.html', pokemonData=pokemon_data, selectedPokemon=selectedPokemon,
                           selectedType1=selectedType1, selectedType2=selectedType2)

@app.route('/suggestions')
def get_suggestions():
    term = request.args.get('term', '')
    selectedType1 = request.args.get('type1')
    selectedType2 = request.args.get('type2')

    with get_connection() as connection, connection.cursor() as cursor:
        query = "SELECT DISTINCT Pokemon FROM pokemon_values WHERE Pokemon LIKE %s"
        params = [f"{term}%"]

        if selectedType1:
            query += " AND Type1 = %s"
            params.append(selectedType1)

        if selectedType2:
            query += " AND Type2 IS NULL"

        query += " ORDER BY Pokemon;"
        cursor.execute(query, params)

        suggestions = [result['Pokemon'] for result in cursor.fetchall()]
        return jsonify(suggestions)

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    term = request.args.get('term', '')
    with get_connection() as connection, connection.cursor() as cursor:
        query = "SELECT DISTINCT Pokemon FROM pokemon_values WHERE Pokemon LIKE %s ORDER BY Pokemon;"
        cursor.execute(query, (f"{term}%",))
        suggestions = [result['Pokemon'] for result in cursor.fetchall()]
        return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True)
