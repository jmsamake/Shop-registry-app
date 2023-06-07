$(document).ready(function() {
  var addSalesRowBtn = $('#addRowBtn');
  var addExpenseRowBtn = $('#addExpenseRowBtn');

  addSalesRowBtn.on('click', function() {
    var salesTable = $('#myTable');
    var salesRowIndex = salesTable.find('tbody tr').length + 1;
    var newRow = $('<tr></tr>');
    var productSelect = $('select[name="product_sale"]').first().clone();
    var priceInput = $('<input type="number" name="price_sale_' + salesRowIndex + '" class="form-control"/>');
    var quantityInput = $('<input type="number" name="quantity_sale_' + salesRowIndex + '" class="form-control"/>');
    var clientSelect = $('select[name="client_sale"]').first().clone();
    var deleteBtn = $('<button class="btn btn-danger deleteRowBtn"><i class="fas fa-times"></i></button>');

    newRow.append($('<td></td>').append(productSelect));
    newRow.append($('<td></td>').append(priceInput));
    newRow.append($('<td></td>').append(quantityInput));
    newRow.append($('<td></td>').append(clientSelect));
    newRow.append($('<td></td>').append(deleteBtn));

    salesTable.find('tbody').append(newRow);
  });

  addExpenseRowBtn.on('click', function() {
    var expenseTable = $('#expenseTable');
    var expenseRowIndex = expenseTable.find('tbody tr').length + 1;
    var newRow = $('<tr></tr>');
    var productSelect = $('select[name="exp_product"]').first().clone();
    var costInput = $('<input type="number" name="exp_cost_' + expenseRowIndex + '" class="form-control" step="0.01"/>');
    var deleteBtn = $('<button class="btn btn-danger deleteExpenseRowBtn"><i class="fas fa-times"></i></button>');

    newRow.append($('<td></td>').append(productSelect));
    newRow.append($('<td></td>').append(costInput));
    newRow.append($('<td></td>').append(deleteBtn));

    expenseTable.find('tbody').append(newRow);
  });

  $(document).on('click', '.deleteRowBtn', function() {
    $(this).closest('tr').remove();
  });

  $(document).on('click', '.deleteExpenseRowBtn', function() {
    $(this).closest('tr').remove();
  });

  $('form#registry_web_form').on('submit', function(event) {
    event.preventDefault();

    var formData = $(this).serialize();

    var salesTableData = [];
    var salesTableRows = $('#myTable tbody tr');
    salesTableRows.each(function(index, row) {
      var rowData = {};
      rowData['product_sale'] = $(row).find('select[name="product_sale"]').val();
      rowData['price_sale'] = $(row).find('input[name^="price_sale"]').val();
      rowData['quantity_sale'] = $(row).find('input[name^="quantity_sale"]').val();
      rowData['client_sale'] = $(row).find('select[name="client_sale"]').val();
      salesTableData.push(rowData);
    });
    formData += '&sales_table_data=' + JSON.stringify(salesTableData);

    var expenseTableData = [];
    var expenseTableRows = $('#expenseTable tbody tr');
    expenseTableRows.each(function(index, row) {
      var rowData = {};
      rowData['exp_product'] = $(row).find('select[name="exp_product"]').val();
      rowData['exp_cost'] = $(row).find('input[name^="exp_cost"]').val();
      expenseTableData.push(rowData);
    });
    formData += '&expense_table_data=' + JSON.stringify(expenseTableData);

    $.ajax({
      url: '/registries/create',
      type: 'POST',
      data: formData,
      success: function(response) {
        // Handle the response from the controller
        console.log(response, 'response');
        // Add your custom logic here
      },
      error: function(xhr, status, error) {
        // Handle the error
        console.error('error', error);
        // Add your error handling logic here
      }
    });
  });
});
