How it Works
============

This package uses `FastAPI Users <https://fastapi-users.github.io/fastapi-users/>`_ to create an extended :class:`msdss_base_api:msdss_base_api.core.API` application.

Database connection variables and engine are handled by :class:`msdss_base_database:msdss_base_database.core.Database` while async database objects are provided by `databases <https://pypi.org/project/databases/>`_.

In order to create a ``FastAPIUsers`` object, this package follows the configuration instructions `here <https://fastapi-users.github.io/fastapi-users/configuration/overview/>`_, where user :any:`msdss_users_api.models`, `authentication objects <https://fastapi-users.github.io/fastapi-users/configuration/authentication/>`_, and database connections are passed as inputs.

.. digraph:: methods

   compound=true;
   rankdir=TB;
   graph [pad="0.75", nodesep="0.25", ranksep="1.15"];

   usermodel[label="User" shape=rect];
   usercreatemodel[label="UserCreate" shape=rect];
   userupdatemodel[label="UserUpdate" shape=rect];
   userdbmodel[label="UserDB" shape=rect];
   usertablemodel[label="UserTable" shape=rect];
   usermanagermodel[label="UserManager" shape=rect];

   fastapifunc[label="create_fastapi_users_objects" shape=rect style=rounded];
   userdbfunc[label="create_user_db_func" shape=rect style=rounded];
   usermanagerfunc[label="create_user_manager_func" shape=rect style=rounded];
   getusersrouter[label="get_users_router" shape=rect style=rounded];

   jwtauth[label="JWTAuthentication" shape=rect];
   cookieauth[label="CookieAuthentication" shape=rect];

   baseapi[label="msdss-base-api" style=filled];
   basedb[label="msdss-base-database" style=filled];
   databases[label="databases" style=filled];
   fastapiusers[label="FastAPI Users" style=filled];

   subgraph cluster0 {
      label=< <B>msdss_users_api.core.UsersAPI</B> >;

      style=rounded;

      subgraph cluster1 {
         label=< <B>msdss_users_api.tools</B> >;
         userdbfunc -> usermanagerfunc -> fastapifunc;
      }
      {basedb;databases} -> userdbfunc[lhead=cluster1 ltail=cluster1];
      usermanagerfunc -> fastapiusers[lhead=cluster1 ltail=cluster1];

      subgraph cluster2 {
         label=< <B>msdss_users_api.models</B> >;
         usermodel;
         usercreatemodel;
         userupdatemodel;
         userdbmodel;
         usertablemodel;
         usermanagermodel;
      };
      usermanagermodel -> usermanagerfunc[lhead=cluster1 ltail=cluster2];
      
      subgraph cluster3 {
          label=< <B>fastapi_users.authentication</B> >;
         jwtauth;
         cookieauth;
      }
      cookieauth -> usermanagerfunc[lhead=cluster1 ltail=cluster3];

      fastapiusers -> getusersrouter -> baseapi;
   }

The command line uses methods from the `FastAPI UsersManager <https://github.com/fastapi-users/fastapi-users/blob/master/fastapi_users/manager.py>`_ to `programmatically manage users <https://fastapi-users.github.io/fastapi-users/cookbook/create-user-programmatically/>`_.

Most of these are implemented under the :mod:`msdss_users_api.tools` module, and run using :func:`msdss_users_api.cli.run`.

.. digraph:: methods

   rankdir=TB;

   deleteuserfunc[label="delete_user (delete)" shape=rect style=rounded];
   getuserfunc[label="get_user (get)" shape=rect style=rounded];
   registeruserfunc[label="register_user (register)" shape=rect style=rounded];
   resetuserfunc[label="reset_user_password (reset)" shape=rect style=rounded];
   updateuserfunc[label="update_user (update)" shape=rect style=rounded];

   subgraph cluster0 {
      label=< <B>msdss_users_api.cli.run</B> >;

      style=rounded;

      subgraph cluster1 {
         label=< <B>msdss_users_api.tools</B> >;
         rankdir=TB;
         deleteuserfunc;
         getuserfunc;
         registeruserfunc;
         resetuserfunc;
         updateuserfunc;
      };

      usersapi[label="msdss_users_api.core.UsersAPI (start)" shape=rect];  

   }