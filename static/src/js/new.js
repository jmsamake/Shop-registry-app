$(document).ready(function() {
  const $tableBody = $('#myTable tbody');
  const $addRowBtn = $('#addRowBtn');

  $addRowBtn.on('click', function() {
    const $newRow = $('<tr>');

    const newProductId = 'product_' + $tableBody.children().length;
    const newPriceId = 'price_' + $tableBody.children().length;
    const newQuantityId = 'quantity_' + $tableBody.children().length;
    const newClientId = 'client_' + $tableBody.children().length;

    // $.ajax({
    //   url: '/get_products_data', //replace with the URL of your controller action that returns product data
    //   type: 'GET',
    //   dataType: 'json',
    //   success: function(data) {
    //     const productOptions = data.map(function(product) {
    //       return `<option value="${product.id}">${product.name}</option>`;
    //     }).join('');
    //
    //     $newRow.html(`
    //       <td>
    //         <select name="product" id="${newProductId}" class="form-control">
    //           <option value="">Select Product</option>
    //           ${productOptions}
    //         </select>
    //       </td>
    //       <td><input type="number" name="${newPriceId}" id="${newPriceId}" step="0.01" class="form-control"/></td>
    //       <td><input type="number" name="${newQuantityId}" id="${newQuantityId}" class="form-control"/></td>
    //       <td>
    //         <select name="client" class="form-control" id="${newClientId}">
    //           <option value="">Select Client</option>
    //           <option value="1">Client A</option>
    //           <option value="2">Client B</option>
    //           <option value="3">Client C</option>
    //         </select>
    //       </td>
    //     `);
    //
    //     $tableBody.append($newRow);
    //   },
    //   error: function(jqXHR, textStatus, errorThrown) {
    //     console.error('Error retrieving product data:', errorThrown);
    //   }
    // });
  });
});
