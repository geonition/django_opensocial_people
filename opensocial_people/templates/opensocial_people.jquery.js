
gnt['opensocial_people'] = {};

/*
This function retrives a list of person objects. The list of people
that is returned has a connection from user and belongs to group.

*/
gnt.opensocial_people['get_list_of_persons'] =
function(user, group, callback_function) {
    
    $.ajax({
        url: "{% url people %}/" + user + "/" + group,
        type: "GET",
        contentType: "application/json",
        success: function(data){
            if(callback_function !== undefined) {
                callback_function(data);
                }
            },
        error: function(e) {
            if(callback_function !== undefined) {
                callback_function(e);
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
        success: function(data){
            if(callback_function !== undefined) {
                callback_function(data);
                }
            },
        error: function(e) {
            if(callback_function !== undefined) {
                callback_function(e);
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
        success: function(data){
            if(callback_function !== undefined) {
                callback_function(data);
                }
            },
        error: function(e) {
            if(callback_function !== undefined) {
                callback_function(e);
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
        success: function(data){
            if(callback_function !== undefined) {
                callback_function(data);
                }
            },
        error: function(e) {
            if(callback_function !== undefined) {
                callback_function(e);
            }
        },
        dataType: "json",
        beforeSend: function(xhr){
            //for cross site authentication using CORS
            xhr.withCredentials = true;
            }
    });
};
