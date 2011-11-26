
gnt['opensocial_people'] = {};

/*
This function retrives a list of person objects. The list of people
that is returned has a connection from user and belongs to group.

If the user is set as @all and the group as @self
it will retrieve all users.

If you want to put additional restrictions you can add
limiting parameters to the group e.g. @self?age=40&married=true

*/
gnt.opensocial_people['get_list_of_persons'] =
function(user, group, callback_function) {
    
    $.ajax({
        url: "{% url people %}/" + user + "/" + group,
        type: "GET",
        contentType: "application/json",
        success: function(data, textStatus, jqXHR){
            if(callback_function !== undefined) {
                callback_function(data, textStatus, jqXHR);
                }
            },
        error: function(jqXHR, textStatus, errorThrown) {
            if(callback_function !== undefined) {
                callback_function(jqXHR, textStatus, errorThrown);
            }
        },
        dataType: "json",
        beforeSend: function(xhr){
            //for cross site authentication using CORS
            xhr.withCredentials = true;
            }
    });
};

/*
 This function retrieves one person object from the server.
 The argument given is the user name which is unique.
 
*/
gnt.opensocial_people['get_person'] =
function(user, callback_function) {
    
    if(user === undefined) {
        user = '@me';
    }
    
    gnt.opensocial_people.get_list_of_persons(user,
                                              '@self',
                                              callback_function);
};

/*
 This function updates the information of a person with the unique
 username,
*/
gnt.opensocial_people['update_person'] =
function(user, person_object, callback_function) {
    
    $.ajax({
        url: "{% url people %}/" + user + "/@self",
        type: "PUT",
        data: JSON.stringify(person_object),
        contentType: "application/json",
        success: function(data, textStatus, jqXHR) {
            if(callback_function !== undefined) {
                callback_function(data, textStatus, jqXHR);
                }
            },
        error: function(jqXHR, textStatus, errorThrown) {
            if(callback_function !== undefined) {
                callback_function(jqXHR, textStatus, errorThrown);
            }
        },
        dataType: "json",
        beforeSend: function(xhr) {
            //for cross site authentication using CORS
            xhr.withCredentials = true;
            }
    });
};

/*
 This function returns a array of key names
 or a JSON object where keys are connected
 with the type of the value.
 
 The types follow the JSON types defined
 at json.org
*/
gnt.opensocial_people['get_supported_fields'] =
function(with_values, callback_function) {
    
    if(with_values === undefined) {
        with_values = false;
    }
    $.ajax({
        url: "{% url people %}/@supportedFields?types=" + with_values,
        type: "GET",
        contentType: "application/json",
        success: function(data, textStatus, jqXHR){
            if(callback_function !== undefined) {
                callback_function(data, textStatus, jqXHR);
                }
            },
        error: function(jqXHR, textStatus, errorThrown) {
            if(callback_function !== undefined) {
                callback_function(jqXHR, textStatus, errorThrown);
            }
        },
        dataType: "json",
        beforeSend: function(xhr){
            //for cross site authentication using CORS
            xhr.withCredentials = true;
            }
    });    
}

/*
 This function creates a relationship between two persons
*/
gnt.opensocial_people['create_relationship'] =
function(initial_user,
         group,
         target_user_person_object,
         callback_function) {
    
    $.ajax({
        url: "{% url people %}/" + initial_user + "/" + group,
        type: "POST",
        data: JSON.stringify(target_user_person_object),
        contentType: "application/json",
        success: function(data, textStatus, jqXHR){
            if(callback_function !== undefined) {
                callback_function(data, textStatus, jqXHR);
                }
            },
        error: function(jqXHR, textStatus, errorThrown) {
            if(callback_function !== undefined) {
                callback_function(jqXHR, textStatus, errorThrown);
            }
        },
        dataType: "json",
        beforeSend: function(xhr){
            //for cross site authentication using CORS
            xhr.withCredentials = true;
            }
    });
};


/*
 This function deletes a relationship
*/
gnt.opensocial_people['delete_relationship'] =
function(initial_user,
         group,
         target_user,
         callback_function) {
    
    $.ajax({
        url: "{% url people %}/" + initial_user + "/" + group + "/" + target_user,
        type: "DELETE",
        contentType: "application/json",
        success: function(data, textStatus, jqXHR){
            if(callback_function !== undefined) {
                callback_function(data, textStatus, jqXHR);
                }
            },
        error: function(jqXHR, textStatus, errorThrown) {
            if(callback_function !== undefined) {
                callback_function(jqXHR, textStatus, errorThrown);
            }
        },
        dataType: "json",
        beforeSend: function(xhr){
            //for cross site authentication using CORS
            xhr.withCredentials = true;
            }
    });
};
