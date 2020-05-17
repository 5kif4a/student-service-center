var faculties = document.getElementById("faculties").value.split("'").join("");
faculties = faculties.replace("[", "");
faculties = faculties.replace("]", "");

var students_by_faculties = document.getElementById("students_by_faculties").value.split("'").join("");
students_by_faculties = students_by_faculties.replace("[", "");
students_by_faculties = students_by_faculties.replace("]", "");

var students_count = document.getElementById("students_count").value;

var students_by_form = document.getElementById("students_by_form").value.split("'").join("");
students_by_form = students_by_form.replace("[", "");
students_by_form = students_by_form.replace("]", "");

var courses = document.getElementById("courses").value.split("'").join("");
courses = courses.replace("[", "");
courses = courses.replace("]", "");

var students_by_courses = document.getElementById("students_by_courses").value.split("'").join("");
students_by_courses = students_by_courses.replace("[", "");
students_by_courses = students_by_courses.replace("]", "");

var ctx = document.getElementById('chart0');
    var myChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: faculties.split(","),
        datasets: [{
            label: '# of Votes',
            data: students_by_faculties.split(","),
            backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"]
        }]
    },
    options: {
        title: {
            display: true,
            text: 'Количество студентов по факультетам'
        }
    }
});

new Chart(document.getElementById("chart1"), {
    type: 'pie',
    data: {
      labels: ["Очная", "Заочная"],
      datasets: [{
        label: "Студенты",
        backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
        data: students_by_form.split(",")
      }]
    },
    options: {
      title: {
        display: true,
        text: 'Количество студентов по форме обучения'
      }
    }
});

new Chart(document.getElementById("chart2"), {
    type: 'doughnut',
    data: {
      labels: courses.split(","),
      datasets: [
        {
          label: "Студенты",
          backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
          data: students_by_courses.split(",")
        }
      ]
    },
    options: {
      title: {
        display: true,
        text: 'Количество студентов по курсам'
      }
    }
});


new Chart(document.getElementById("chart3"), {
    type: 'horizontalBar',
    data: {
      labels: ["Africa", "Asia", "Europe", "Latin America", "North America"],
      datasets: [
        {
          label: "Population (millions)",
          backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
          data: [2478,5267,734,784,433]
        }
      ]
    },
    options: {
      legend: { display: false },
      title: {
        display: true,
        text: 'Predicted world population (millions) in 2050'
      }
    }
});
