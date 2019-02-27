function get_scores() {
  getJSON('/scoreboard.json/', function(err, data) {
    var scoreboard = $("#scoreboard");
    scoreboard.empty();
    for (i = data.length -1; i >= 0; i--) {
      entry = `
        <tr>
          <td scope="row">${i+1}</td>
          <td><a href="/team/${data[i]._id}">${data[i].name}</a></td>
          <td>${data[i].score}</td>
        </tr>
      `;
      scoreboard.prepend(entry);
    }
  });
  setTimeout(get_scores, 5000);
}
get_scores();
