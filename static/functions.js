function help()
{
    alert("\nYou can help us by spreading the word!\n\nPlease share this website!")
}

/* The following function was extracted from: /* Part of the following calculator was created using the following as a guide: view-source:https://dolartoday.com/calculadora/*/
function formatCurrency(num) {
        num = num.toString().replace(/\$|\,/g, '');
        if (isNaN(num)) num = "0";
        sign = (num == (num = Math.abs(num)));
        num = Math.floor(num * 100 + 0.50000000001);
        cents = num % 100;
        num = Math.floor(num / 100).toString();
        if (cents < 10) cents = "0" + cents;
        for (var i = 0; i < Math.floor((num.length - (1 + i)) / 3); i++)
                num = num.substring(0, num.length - (4 * i + 3)) + '.' + num.substring(num.length - (4 * i + 3));
        return (((sign) ? '' : '-') + num + ',' + cents);
}

function calculate()
{
    let euros = document.querySelector("#euros").value;
    let rate = document.querySelector("#rate").value;
    let bs = euros * rate;

    /* Change the input text value property: https://www.w3schools.com/jsref/prop_text_value.asp;*/
    document.getElementById("bs").value = formatCurrency(bs);
}

/* Sort a table: https://www.w3schools.com/howto/howto_js_sort_table.asp*/

function sortTable()
{
  var table, rows, switching, i, x, y, shouldSwitch;
  table = document.getElementById("bankAccounts");
  switching = true;
  /* Make a loop that will continue until no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the first, which contains table headers): */
    for (i = 1; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare, one from current row and one from the next: */
      x = rows[i].getElementsByTagName("TD")[0];
      y = rows[i + 1].getElementsByTagName("TD")[0];
      // Check if the two rows should switch place:
      if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
        // If so, mark as a switch and break the loop:
        shouldSwitch = true;
        break;
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
    }
  }
}