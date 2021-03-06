from flask import Flask, g, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = 'netball.db'

def get_db():
    db = getattr(g,'_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g,'_database', None)
    if db is not None:
        db.close()

#home route with the names of the players
@app.route("/")
def home():
    cursor = get_db().cursor()
    sql = "SELECT id, Name FROM Player ORDER BY Name"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("player.html", results=results)

#route to show each players positions
@app.route("/positions")
def Positions():
    cursor = get_db().cursor()
    sql = "SELECT Player.Name, Positions.Positions FROM PLAYER JOIN PlayerPositions ON Player.id = PlayerPositions.Player_id JOIN Positions ON PlayerPositions.Positions_id = Positions.id ORDER BY Name;"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("player_positions.html", results=results)

#route to show how many trainings each player has been to
@app.route("/trainings")
def Trainings():
    cursor = get_db().cursor()
    sql = "SELECT Player.Name, Player.Trainings FROM Player ORDER BY Name;"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("trainings.html", results=results)

#route to show how many wins each player has contributed to
@app.route("/wins")
def Wins():
    cursor = get_db().cursor()
    sql = "SELECT Player.Name, Player.Wins FROM Player ORDER BY Name;"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("wins.html", results=results)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        #add player information to the database
        cursor = get_db().cursor()
        new_player_name = request.form["new_player_name"]
        new_player_trainings = request.form["new_player_trainings"]
        new_player_wins = request.form["new_player_wins"]
        sql = "INSERT INTO Player(Name, Trainings, Wins) VALUES (?,?,?);"   
        cursor.execute(sql,(new_player_name, new_player_trainings, new_player_wins))
        position1 = request.form["Position1"]
        position2 = request.form["Position2"]
        position3 = request.form["Position3"]
        new_player_id = cursor.lastrowid
        sql = "INSERT INTO PlayerPositions(Positions_id, Player_id) VALUES (?,?);"
        cursor.execute(sql, (position1, new_player_id))
        sql = "INSERT INTO PlayerPositions(Positions_id, Player_id) VALUES (?,?);"
        cursor.execute(sql, (position2, new_player_id))
        sql = "INSERT INTO PlayerPositions(Positions_id, Player_id) VALUES (?,?);"
        cursor.execute(sql, (position3, new_player_id))
        get_db().commit()
        return redirect ("/")
    return render_template("add_player.html")


@app.route("/player/<int:id>")
def player(id):
    #dynamic route for each player showing their information
    cursor = get_db().cursor()
    sql = "SELECT Player.Name FROM Player WHERE Player.id = ?"
    cursor.execute(sql, (id,))
    player = cursor.fetchone()    
    sql = "SELECT Positions.Positions FROM PLAYER JOIN PlayerPositions ON Player.id = PlayerPositions.Player_id JOIN Positions ON PlayerPositions.Positions_id = Positions.id WHERE Player.id = ?;"
    cursor.execute(sql, (id,))
    positions = cursor.fetchall()
    sql = "SELECT Player.Wins FROM Player WHERE Player.id = ?"
    cursor.execute(sql, (id,))
    wins = cursor.fetchone()    
    sql = "SELECT Player.Trainings FROM Player WHERE Player.id = ?"
    cursor.execute(sql, (id,))
    trainings = cursor.fetchone()
    return render_template("player_route.html", player=player, wins=wins, positions=positions, trainings=trainings)

@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        #get the item and delete from database
        cursor = get_db().cursor()
        id = int(request.form["player_name"])
        sql = "DELETE FROM Player WHERE id=?"
        cursor.execute(sql,(id,))
        get_db().commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
