/////////////////////////////
//////// LIST HEADER ////////
/////////////////////////////

// Pagination
$(document).on("click", ".page-link", function (event) {
    event.preventDefault();
    window.history.pushState(null, "", updateQueryStringParameter(location.search, "page", $(this).data("page")));
    window.scrollTo(0, 0);

    fetchTable(location.search.substring(1));
});

// Sort order
$(document).on("change", ".sort-order-link", function(event){
    event.preventDefault();
    window.history.pushState(null, "", updateQueryStringParameter(location.search, "so", $(this).val()));
    window.history.pushState(null, "", updateQueryStringParameter(location.search, "page", 1));

    fetchTable(location.search.substring(1));
});

// Display type
$(document).on("change", ".display-type-link", function(event){
    event.preventDefault();
    window.history.pushState(null, "", updateQueryStringParameter(location.search, "dt", $(this).val()));
    window.scrollTo(0, 0);

    fetchTable(location.search.substring(1));
});

/////////////////////////////
/////// GENERIC TABLE ///////
/////////////////////////////

const tableWrapperId = "#table-wrapper";
let tableType;

// Fetch the previous table when the state changes (back button/forward button)
window.onpopstate = function () {
    fetchTable(location.search.substring(1));
};

function initializeTable(tt) {
    tableType = tt;

    // Load the first table and apply query filters if available in the link
    if (isEmpty(location.search)) {
        fetchTable(null);
    } else {
        fetchTable(location.search.substring(1));

        // If there are any existing filters (e.g. from sharing a URL), fill in the UI filters with data
        fillForm();
    }
}

// Fetch html for the new table
function fetchTable(data) {
    $.ajax({
        url: "/" + tableType + "/ajax/table",
        type: "GET",
        data: data,

        success: function (html) {
            $(tableWrapperId).empty();
            $(tableWrapperId).append(html)
        },

        error: function (xhr, errmsg, err) {
        }
    });
}

/////////////////////////////
////////// FILTER ///////////
/////////////////////////////
function analyzeForm() {
    let queryParams = [];

    if (!isEmpty(location.search)) {
        queryParams = queryStringToDictionary(location.search);
    }

    function updateQueryParams(parameterName, parameterValue) {
        if (!isEmpty(parameterValue)) {
            let exists = false;

            // Check if there is a previous filter to update and if so, update that filter instead of creating a new one
            for (let i in queryParams) {
                if (parameterName === queryParams[i].name) {
                    exists = true;
                    queryParams[i].value = parameterValue;
                    break;
                }
            }

            // There isn't a previous filter to update, just create a new one
            if (!exists) {
                queryParams.push({
                    name: parameterName,
                    value: parameterValue
                })
            }
        }
        else {
            // If there was a previous filter for this item, but there isn't any now, remove it
            for (let i in queryParams) {
                if (parameterName === queryParams[i].name) {
                    queryParams.splice(i, 1);
                    break;
                }
            }
        }
    }

    // Check select2 filters
    $('.select2-widget').each(function(i, obj) {
        let parameterName = obj.name;
        let parameterValue = generateSelect2CheckboxParameter(parameterName);

        updateQueryParams(parameterName, parameterValue);
    });

    // Check normal select filters
    $('.select').each(function(i, obj) {
        let parameterName = obj.name;
        let parameterValue = obj.options[obj.selectedIndex].value;

        updateQueryParams(parameterName, parameterValue);
    });

    // Check the text filters
    $(".filter-sidebar input[type=text]").each(function() {
        let parameterName = this.name;
        let parameterValue = this.value;

        updateQueryParams(parameterName, parameterValue);
    });

    // Remove pagination because the filter changed
    for (let i in queryParams) {
        if (queryParams[i].name === "page") {
            queryParams.splice(i, 1);
            break;
        }
    }

    window.history.pushState(null, "", "?" + $.param(queryParams).replace(/%2C/g, ","));
    fetchTable(location.search.substring(1))
}

function fillForm() {
    let queryParams = queryStringToDictionary(location.search);

    for (let queryParam in queryParams) {
        const paramName = queryParams[queryParam].name;
        const paramValue = queryParams[queryParam].value;

        if (paramName !== "page" && paramName !== "so" && paramName !== "dt") {
            const values = paramValue.split(",");
            $("#id_" + paramName).val(values)
        }
    }
}

// Generate a query parameter for a multi-checkbox filter
function generateSelect2CheckboxParameter(filterName) {
    let selectedItems = $("#id_" + filterName).select2("data");
    let queryItems = [];

    for (let i in selectedItems) {
        queryItems.push(selectedItems[i].id);
    }

    return queryItems.join();
}

/////////////////////////////
///// GENERAL UTILITIES /////
/////////////////////////////

// Create or update a query parameter
function updateQueryStringParameter(uri, key, value) {
    let re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
    let separator = uri.indexOf('?') !== -1 ? "&" : "?";

    if (uri.match(re)) {
        return uri.replace(re, '$1' + key + "=" + value + '$2');
    }
    else {
        return uri + separator + key + "=" + value;
    }
}

function queryStringToDictionary(queryString) {
    var dictionary = [];

    // remove the '?' from the beginning if it exists
    if (queryString.indexOf('?') === 0) {
        queryString = queryString.substr(1);
    }

    // Step 1: separate out each key/value pair
    var parts = queryString.split('&');

    for (var i = 0; i < parts.length; i++) {
        var p = parts[i];
        // Step 2: Split Key/Value pair
        var keyValuePair = p.split('=');

        // Step 3: Add Key/Value pair to Dictionary object
        var key = keyValuePair[0];
        var value = keyValuePair[1];

        // decode URI encoded string
        value = decodeURIComponent(value);
        value = value.replace(/\+/g, ' ');

        dictionary.push({
            name: key,
            value: value
        })
    }

    // Step 4: Return Dictionary Object
    return dictionary;
}

// Check if a value is empty
function isEmpty(value) {
    return value == null || value === "";
}