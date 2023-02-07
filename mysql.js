var BASE_URL = "http://127.0.0.1:5432/mysql";

function init_explorer() {
  axios.get(BASE_URL + "/ls", {
    params: {
      path: "/user"
    }
  })
    .then(function (response) {
      // handle success
      console.log(response);

      populate_tree(response);
      render_explorer_tree();
    })
    .catch(function (error) {
      // handle error
      console.log(error);
    });
}

function populate_tree(response) {
  // clear tree view
  explorerList.empty();

  dirs = response.data["directories"];
  files = response.data["files"];

  var tree = "";

  if (dirs) {
    for (var i = 0; i < dirs.length; i++) {
      tree += "<li><span><i class='fa-solid fa-folder' data-path='' onClick='do_ls(this);'></i> " + dirs[i] + " </span>";
    }
  }

  if (files) {
    for (var i = 0; i < files.length; i++) {
      if (files[i] === ".") {
        continue;
      }
      tree += "<span><i class='fa-regular fa-file'></i> " + files[i] + " </span>";
    }
  }

  explorerList.append(tree);

  if(explorerList.children().length == 0) {
    explorerList.append("<p class='text-center'>This directory is empty</p>");
  }
}

// tree view
function render_explorer_tree() {
  $(".tree li:has(ul)")
    .addClass("parent_li")
    .find(" > span")
    .attr("title", "Collapse this branch");
  $(".tree li.parent_li > span").on("click", function (e) {
    var children = $(this).parent("li.parent_li").find(" > ul > li");
    if (children.is(":visible")) {
      children.hide("fast");
      $(this).attr("title", "Expand this branch").find(" > i");
    } else {
      children.show("fast");
      $(this).attr("title", "Collapse this branch").find(" > i");
    }
    e.stopPropagation();
  });
}

// ls
function do_ls(path) {
  axios.get(BASE_URL + '/ls', {
    params: {
      path: path
    }
  })
    .then(function (response) {
      // handle success
      console.log(response);
      // $("#sample").text(JSON.stringify(response.data));
      $("#ls").text(JSON.stringify(response.data))
      retrieved_response = response

      populate_tree(response);
      render_explorer_tree();
    })
    .catch(function (error) {
      // handle error
      console.log(error);
    })
}

function mkdir(path) {
  axios.get(BASE_URL + '/mkdir', {
    params: {
      path: path
    }
  })
    .then(function (response) {
      // handle success
      console.log(response);
      data = response.data;
      alert(data.status);
    })
    .catch(function (error) {
      console.log(error);
    })
}

// cat

function cat(path) {
  axios.get(BASE_URL + '/cat', {
    params: {
      file: path
    }
  })
    .then(function (response) {
      console.log(response);
      var data = response.data;
      var decode_data = [];
      for (let i = 0; i < data.length; i++) {
        decode_data.push(JSON.parse(data[i]));
      }

      var html = "<table class='table table-stripped'><thead>";

      var table_headings = Object.keys(decode_data[0]);
      for (let i = 0; i < table_headings.length; i++) {
        html += "<th>" + table_headings[i] + "</th>";
      }

      html += "</thead><tbody>"

      for (let i = 0; i < decode_data.length; i++) {
        var row = "<tr>";
        for (const prop in decode_data[i]) {
          row += "<td>" + decode_data[i][prop] + "</td>";
        }
        row += "</tr>";
        html += row;
      }

      html += "</tbody></table>"
      $("#fileContent").empty();
      $("#fileContent").append(html);

    })
    .catch(function (error) {
      console.log(error);
    }).then(function () {
      getPartitionLocations(path);
    });
}




// rm
function rm(path) {
  axios.get(BASE_URL + '/rm', {
    params: {
      path: path
    }
  })
    .then(function (response) {
      // handle success
      console.log(response);
      // $("#sample").text(JSON.stringify(response.data));
      alert(response.data.status);
    })
    .catch(function (error) {
      console.log(error);
    });
}


// getpartitionLocations
function getPartitionLocations(path) {
  axios.get(BASE_URL + '/getpartitionLocations', {
    params: {
      file: path
    }
  })
    .then(function (response) {
      // handle success
      console.log(response);
      // $("#sample").text(JSON.stringify(response.data));
      // $("#getpartitionLocations").text(JSON.stringify(response.data))
      // retrieved_response = response
      var partitionsBody = $("#partitionsBody");
      var rows = "";
      for (var prop in response.data) {
        rows += "<tr><td>" + prop + "</td><td>" + response.data[prop] + "</td></tr>";
      }
      partitionsBody.empty();
      partitionsBody.append(rows);
    })
    .catch(function (error) {
      console.log(error);
    });
}


// readPartition
function readPartition(path, partition) {
  axios.get(BASE_URL + '/readPartition', {
    params: {
      file: path,
      partNumber: partition
    }
  })
    .then(function (response) {
      // handle success
      console.log(response);

      var data = response.data;

      var decode_data = [];
      for (let i = 0; i < data.length; i++) {
        decode_data.push(JSON.parse(data[i]));
      }

      var html = "<table class='table table-stripped'><thead>";

      var table_headings = Object.keys(decode_data[0]);
      for (let i = 0; i < table_headings.length; i++) {
        html += "<th>" + table_headings[i] + "</th>";
      }

      html += "</thead><tbody>"

      for (let i = 0; i < decode_data.length; i++) {
        var row = "<tr>";
        for (const prop in decode_data[i]) {
          row += "<td>" + decode_data[i][prop] + "</td>";
        }
        row += "</tr>";
        html += row;
      }

      html += "</tbody></table>";
      $("#partitionContent").empty();
      $("#partitionContent").append(html);

      retrieved_response = response;
    })
    .catch(function (error) {
      console.log(error);
    });
}


function put(payload) {
  // put
  axios.post(BASE_URL + '/put', payload, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
})
    .then(function (response) {
      // handle success
      console.log(response);
      alert(JSON.stringify(response.data.status));
    })
    .catch(function (error) {
      console.log(error);
    });
}

// Search
function searchDeathPerCountry(resultDiv, payload) {
  console.log(payload);
  axios.get(BASE_URL + '/countrydeathcount', {
    params: payload
  })
    .then(function (response) {
      // handle success
      console.log(response);
      // alert(JSON.stringify(response.data));
      resultDiv.empty();
      resultDiv.append(response.data);
    })
    .catch(function (error) {
      console.log(error);
    });
}

function searchNoOfCasesByCountry(resultDiv, payload) {
  axios.get(BASE_URL + '/findcountriesbetween', {
    params: payload
  })
  .then(function (response) {
    // handle success
    // alert(JSON.stringify(response.data));
    var data = response.data;
    
    if(data.length > 0) {
      var result="<table class='table table-stripped'><thead><th>Country</th><th>Cases</th><tbody>";


      for (var i = 0; i < data.length; i++) {
        var row = "<tr>";
  
        item = JSON.parse(data[i]);
        row += "<td>" + item["country"] + "</td>";
        row += "<td>" + item["cases"] + "</td>";
  
        row += "</tr>";
        result += row;
      }
  
  
      result += "</tbody></table>";
    } else {
      var result = "<p class='text-center'>No cases found.</p>"
    }

    resultDiv.empty();
    resultDiv.append(result);
  })
  .catch(function (error) {
    console.log(error);
  });
}


// Analysis
function deathByCountryFunc(resultDiv) {
  axios.get(BASE_URL + '/analysisdeathpercountry')
    .then(function (response) {
      // handle success
      // alert(JSON.stringify(response.data));

      var html="<table class='table table-stripped'><thead><th>Country</th><th>Deaths</th><tbody>";

      data = response.data;

      for (var i = 0; i < data.length; i++) {
        var row = "<tr>";

        item = JSON.parse(data[i]);
        row += "<td>" + item["country"] + "</td>";
        row += "<td>" + item["deaths"] + "</td>";

        row += "</tr>";
        html += row;
      }


      html += "</tbody></table>";

      resultDiv.empty();
      resultDiv.append(html);
    })
    .catch(function (error) {
      console.log(error);
    });
}


function avgRecoveredCasesFunc(resultDiv) {
  axios.get(BASE_URL + '/analysisrecovery')
    .then(function (response) {
      // handle success
      console.log(response);
      // alert(JSON.stringify(response.data));

      data = response.data;

      var mapperData = data["mapper"];

      var mapperHTML = "<h4>Mapper</h4>";

      var datasets = Object.keys(mapperData);
      for (let i = 0; i < datasets.length; i++) {
        var dataset = datasets[i];
        var datasetData = mapperData[dataset];
        datasetHTML = "<h5 class='text-uppercase'>" + dataset + "</h5><table class='table table-stripped'><thead><th>Avg Recovered Cases</th><th>Total Cases</th><tbody>";
        
        for (let j = 0; j < datasetData.length; j++) {
          var rowData = datasetData[j];
          datasetHTML += "<tr><td>" + rowData[0] + "</td><td>" + rowData[1] + "</td></tr>"
        }

        datasetHTML += "</tbody></table>";

        mapperHTML += datasetHTML;
      }


      var reducerHTML="<br><h4>Reducer</h4><table class='table table-stripped'><thead><th>Dataset</th><th>Avg Recovered Cases</th><th>Total Cases</th><tbody>";
      var reducerData = data["reducer"];

      var datasets = Object.keys(reducerData);
      for (let i = 0; i < datasets.length; i++) {
        var dataset = datasets[i];
        reducerHTML += "<tr><td>" + dataset + "</td><td>" + reducerData[dataset][0] + "</td><td>" + reducerData[dataset][1] + "</td></tr>";
      }


      reducerHTML += "</tbody></table>";

      resultDiv.empty();
      resultDiv.append(mapperHTML + reducerHTML);
    })
    .catch(function (error) {
      console.log(error);
    });
}


