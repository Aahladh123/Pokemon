from flask import Flask, render_template, request,jsonify
import pymysql
import pymysql.cursors

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
        with cursor as connection:
            if name_or_number.lower() == 'all':
                query = "SELECT * FROM pokemon_values;"
                cursor.execute(query)
            else:
                try:
                    query = "SELECT * FROM pokemon_values WHERE Ndex = %s OR UPPER(Pokemon) = UPPER(%s);"
                    cursor.execute(query, (name_or_number,name_or_number))
                except:
                    # If conversion to integer fails, assume it's a name
                    query = "SELECT * FROM pokemon_values WHERE UPPER(Pokemon) = UPPER(%s);"
                    cursor.execute(query, (name_or_number.lstrip('#').lstrip('0'),name_or_number))

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

    with get_connection() as connection, connection.cursor() as cursor:
        if request.method == 'POST':
            pokemon_value = request.form['search_term']

            # If the input is a number, pad with leading zeros
            if pokemon_value.isdigit():
                pokemon_value = f"#{int(pokemon_value):04d}"

            pokemon_data = get_pokemon_stats(pokemon_value, cursor)

            # Set selectedPokemon if a specific Pokemon is queried
            if pokemon_data and len(pokemon_data) == 1:
                selectedPokemon = pokemon_data[0]

        else:
            default_pokemon = 'All'
            pokemon_data = get_pokemon_stats(default_pokemon, cursor)

    return render_template('index_v2.0.html', pokemonData=pokemon_data, selectedPokemon=selectedPokemon)

@app.route('/suggestions')
def get_suggestions():
    term = request.args.get('term', '')
    with get_connection() as connection, connection.cursor() as cursor:
        query = "SELECT DISTINCT Pokemon FROM pokemon_values WHERE Pokemon LIKE %s;"
        cursor.execute(query, (f"%{term}%",))
        suggestions = [result['Pokemon'] for result in cursor.fetchall() if result['Pokemon'].lower().startswith(term.lower())]
        return jsonify(suggestions)

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    term = request.args.get('term', '')
    with get_connection() as connection, connection.cursor() as cursor:
        query = "SELECT DISTINCT Pokemon FROM pokemon_values WHERE Pokemon LIKE %s ORDER BY Pokemon;"
        cursor.execute(query, (f"{term}%",))
        suggestions = [result['Pokemon'] for result in cursor.fetchall() if
                       result['Pokemon'].lower().startswith(term.lower())]
        return jsonify(suggestions)


if __name__ == '__main__':
    app.run(debug=True)