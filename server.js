const mysql = require ('mysql2');
const express = require ('express');
const cors = require ('cors');
const path = require('path');
app = express();
// for http connection
app.use(cors());
// to allow access to the public directory for stylesheets and dynamic html with js
app.use(express.static(path.join(__dirname, 'public')));

//connect to the mysql databse 
const connectionPool = mysql.createPool({
    host: '<PlaceHolder>',
    user: '<PlaceHolder>',
    password: '<PlaceHolder>',
    database: '<PlaceHolder>',
    ssl: {
        CA: path.join(__dirname, '<PlaceHolder>')
    },
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0,
});

// get request to retrieve the corresponding selected information from the database
app.get('/api/results/main', (request, response) => {
    let {Season, Level, Event, Gender, Year} = request.query;
    Season = Season.replaceAll('-', ' ');
    Level = Level.replaceAll('-', ' ');
    Event = Event.replaceAll('-', ' ');

    if (Season && Level && Event && Gender && Year){
        connectionPool.query(`SELECT * FROM YEAR${Year} 
            WHERE Season='${Season}' AND Level='${Level}' AND Event='${Event}' AND Gender='${Gender}'
            ORDER BY Mark ;`, (error, results) => {
            if (error) throw error;
            response.json(results);
        });
    } else {
        response.send("INVALID");
    }
});

// gets each category for quicklinks
app.get('/api/results/quicklinks', (request, response) => {
    let {Gender, Year} = request.query;
    if (Gender && Year){
        connectionPool.query(`SELECT DISTINCT Season, Level, Event FROM YEAR${Year} Where Gender='${Gender}'`, (error, results) => {
            if (error) throw error;
            response.json(results);
        })
    } else {
        console.log("Invalid Query");
        response.send('Invalid Query');
    }
})

// shows each table for the years
app.get('/api/tables', (request, response) => {
    connectionPool.query(`  SELECT TABLE_NAME
                        FROM INFORMATION_SCHEMA.tables
                        WHERE TABLE_SCHEMA = 'resultstables'
                        AND TABLE_COMMENT = 'YEAR'
                        ORDER BY TABLE_NAME DESC;`, (error, result) => {
                            if (error) throw error;
                            response.json(result);
    })
})

//default page
app.get('/', (request, response) => {
    response.sendFile(path.join(__dirname, '/public/html/Index.html'))
})

//about page
app.get('/about', (request, response) => {
    response.sendFile(path.join(__dirname, '/public/html/about.html'))
})

//shoes page
app.get('/shoes', (request, response) => {
    response.sendFile(path.join(__dirname, '/public/html/shoes.html'))
})

// starts the server, allows the app to listen the provided port from azure, or 300
const PORT =  process.env.PORT || 8080;
app.listen(8080, () => {
    console.log('Server running on port ' + PORT);
})

