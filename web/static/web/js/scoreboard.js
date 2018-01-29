function get_scores() {
  getJSON('/api/scoreboard/', function(err, data) {
    var scoreboard = $("#scoreboard");
    scoreboard.empty();
    for (i = data.length -1; i >= 0; i--) {
      entry = `
        <tr>
          <td scope="row">${i+1}</td>
          <td><a href="/team/${data[i].team_id}">${data[i].team_name}</a></td>
          <td>${data[i].team_score}</td>
        </tr>
      `;
      scoreboard.prepend(entry);
    }
  });
  setTimeout(get_scores, 5000);
}
get_scores();
