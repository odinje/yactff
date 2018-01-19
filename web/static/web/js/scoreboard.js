getJSON('/api/scoreboard/', 
function(err, data) {
  var scoreboard = $("#scoreboard");
  for (i = data.length -1; i >= 0; i--) {
    entry = `
      <tr>
        <th scope="row">${i+1}</th>
        <th><a href="/team/${data[i].team_id}">${data[i].team_name}</a></th>
        <th>${data[i].team_score}</th>
      </tr>
    `;
    scoreboard.prepend(entry);
  }
});
