const baseURL = "https://hobbyjoggers.net"

// default for when the page opens
const tableHead = document.querySelector('#main-table thead');
tableHead.innerHTML = `<tr><th style="font-size: 5vw;"">Welcome to HobbyJoggers.net!</th></tr>
                       <tr>        
                            <p class="welcome">Welcome to HobbyJoggers.net, your go-to platform for analyzing running results from top sources like 
                            MileSplit, Athletic.net, World Athletics, and NCAA. Powered by Python, our platform leverages 
                            cutting-edge web scraping techniques to collect, organize, and present comprehensive data on track 
                            and field performances, cross-country results, and road races.
                            <br>
                            <br>
                            Whether you’re a coach, athlete, or fan, HobbyJoggers.net simplifies access to the stats you need, 
                            offering insights into trends, rankings, and individual performance progressions. Stay ahead of 
                            the competition with accurate, real-time data—because every second counts.
                            <br>
                            <br>
                            My website dynamically generates webpages using HTML, CSS, and JavaScript on the front end to display
                            running results fetched from the database. On the backend, the server runs Node.js 20 with Express and
                            MySQL2 to handle requests and serve the webpage, while results are scraped primarily from Athletic.net,
                            for now, using Python and stored in a MySQL database. The web app and database are both hosted on 
                            Microsoft Azure with Cloudflare DNS and are deployed with GitHub, ensuring seamless performance and 
                            scalability.
                            <br>
                            <br>
                            In the year selector, 0_example is a table with example information to show how the Quick Links table 
                            is dynamically generated using the information in the database table.
                            <br>
                            <br>
                            Any Questions can be emailed to ghayden433@gmail.com - Hayden Gillen
                            </p></tr>`;

// function to create the html added to the tbody in maintable
function createMainTable(data, query=false) {
    //table head
    const tableHead = document.querySelector('#main-table thead');
    tableHead.innerHTML = '<tr><th>Rank</th><th>Grade</th><th>Name</th><th>Time</th><th>Date</th><th>Results</th></tr>'

    //table body
    // select the tag where this information goes: in the main-table table's tbody tag
    const tableBody = document.querySelector('#main-table tbody');
    let i = 1;
    let HTML = '';
    data.forEach((result) => {
        HTML = HTML +`
            <tr>
                <td>${i}</td>
                <td>${result.Grade}</td>
                <td>${result.Name}</td>
                <td>${result.Mark}</td>
                <td>${result.PerformanceDate}</td>
                <td><a class="button" href="${result.Results}" target=_blank>Results</a></td>
            </tr>
        `;
        i++;
    })
    // now weve created a tr element, add it to the table
    tableBody.innerHTML = HTML;
}

function CreateQuickLinks() {
    // this generates the quicklinks table on the left of server.html
    Gender = document.getElementById('GENDER')
    Gender = Gender.options[Gender.selectedIndex].getAttribute('value');
    Year = document.getElementById('YEAR');
    Year = Year.options[Year.selectedIndex].getAttribute('value');

    fetch(`${baseURL}/api/results/quicklinks?Gender=${Gender}&Year=${Year}`)
        .then((response) => response.json())
        .then((data) => {
            //select quicklinks table
            const tableBody = document.querySelector('.QuickLinks tbody');

            tableBody.innerHTML = "<tr><td>Loading...</td></tr>";

            const seasons = [...new Set(data.map(element => element.Season))];

            // for each season create a nested details/summary tag for each level that occurs in each season
            let HTML = '';
            seasons.forEach((season) => {
                //const row = document.createElement('tr');
                HTML = HTML + `
                    <tr>
                    <td class="linkGroup">
                        <details>
                            <summary class="head">${season}</summary>`;

                let levels = data
                    .filter(element => element.Season === season)        // exctract all the levels that occur in current season
                    .map(element => element.Level);                      // get all of the seasons as an array
                levels = [...new Set(levels.map(element => element))];   // levels is now unique levels within current season

                levels.forEach((level) => { // add a level summary/details tag and then within add the events
                    HTML =  HTML + `
                            <details>
                            <summary class="branch">${level}</summary>`;

                    let events = data
                        .filter(element => element.Season === season && element.Level === level)    // extract all events in current level and season
                        .map(element => element.Event);                                             // turn it into an array
                    events = [...new Set(events.map(element => element))];                          // events is array of unique events

                    events.forEach((event) => {
                        HTML =  HTML + `
                                <p class="leaf" 
                                query-value=Season=${season.replaceAll(' ', '-')}&Level=${level.replaceAll(' ', '-')}&Event=${event.replaceAll(' ', '-')}>
                                ├  ${event}</p>`;
                    
                    // add closing tags
                    })
                    HTML = HTML + `
                            </details>`
                })
                HTML = HTML + `
                        </details>
                    </td>
                    </tr>`;   
            })
            tableBody.innerHTML = HTML;

            const setupButtons = new CustomEvent('buttons')
            document.dispatchEvent(setupButtons);      // triggers the setup of the buttons in quicklinks
        })
    .catch((error) => console.error('Error fetching data:', error));
    
    //IDK but it's trying give the user an inicator when the db won't respond
    //const tableBody = document.querySelector('.QuickLinks tbody');
    //tableBody.innerHTML = `<tr><td>Server Unavaliable</td></tr>
    //                       <tr><td>Please Try Again Later</td></tr>`;
}



// code for the click of each leaf within the quicklinks table
document.addEventListener('buttons', () => {
    const buttons = document.querySelectorAll('.leaf');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            let query = button.getAttribute('query-value');

            const select1 = document.getElementById('GENDER');
            const select1Option = select1.options[select1.selectedIndex]; 
            const gender = select1Option.getAttribute('value');
            
            const select2 = document.getElementById('YEAR');
            const select2Option = select2.options[select2.selectedIndex]; 
            const year = select2Option.getAttribute('value')

            // create table title
            let params = new URLSearchParams(query);
            const values = {};
            for (const [key, value] of params) {
                values[key] = value;
            }
            let title = document.getElementById('title');
            title.innerHTML = `${year} ${values['Level'].replaceAll('-', ' ')} ${values['Season'].replaceAll('-', ' ')} ${Gender} ${values['Event'].replaceAll('-', ' ')}`;
            const tableBody = document.querySelector('#main-table tbody');
            tableBody.innerHTML = '<tr><td colspan="100%" style="font-size:500%">Loading...</td></tr>';

            query = `${query}&Gender=${gender}&Year=${year}`
            const apiURL = (`${baseURL}/api/results/main?${query}`);
            fetch(apiURL)
            .then((response) =>response.json())
            .then((data => {createMainTable(data, true)}));
        })
    })
})

//Generate the select tag for each year
fetch(`${baseURL}/api/tables`)
    .then((response) => {
        return response.json();
    })
    .then((data) => { 
        const select = document.querySelector('#YEAR');
        HTML = '';
        data.forEach(year => {
            year = year.TABLE_NAME.replaceAll('year', '');
            HTML = HTML + `<option value="${year}">${year}</option>`;
        })
        select.innerHTML = HTML;
})
.catch((error) => {
    console.log(error);
    const table = document.querySelector('.QuickLinks tbody');
    table.innerHTML = `<tr><td>Database Unavaliable :(</td></tr>
                       <tr><td>Please Try Again Later</td></tr>`;
})
.then(() => {
    // to generate the table when the page loads with default values
    // only executes once the option tag is filled
    CreateQuickLinks();
})

// re-generates quicklinks when gender or year is changed
const selectElements = document.querySelectorAll('select');

selectElements.forEach(selectElements => {
    selectElements.addEventListener('change', () => CreateQuickLinks());
})