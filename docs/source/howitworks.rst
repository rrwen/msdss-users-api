How it Works
============

This package uses `FastAPI Users <https://fastapi-users.github.io/fastapi-users/>`_ to create an extended :class:`msdss_base_api:msdss_base_api.core.API` application.

Database connection variables and engine are handled by :class:`msdss_base_database:msdss_base_database.core.Database` while async database objects are provided by `databases <https://pypi.org/project/databases/>`_.

In order to create a ``FastAPIUsers`` object, this package follows the configuration instructions `here <https://fastapi-users.github.io/fastapi-users/configuration/overview/>`_, where user :any:`msdss_users_api.models`, `authentication objects <https://fastapi-users.github.io/fastapi-users/configuration/authentication/>`_, and database connections are passed as inputs.

The command line uses methods from the `FastAPI UsersManager <https://github.com/fastapi-users/fastapi-users/blob/master/fastapi_users/manager.py>`_ to `programmatically manage users <https://fastapi-users.github.io/fastapi-users/cookbook/create-user-programmatically/>`_.

.. digraph:: methods

   compound=true;
   rankdir=TB;
   graph [pad="0.75", nodesep="0.25", ranksep="1"];

   usermodel[label="User" shape=rect URL="https://fastapi-users.github.io/fastapi-users/configuration/models/"];
   usercreatemodel[label="UserCreate" shape=rect URL="https://fastapi-users.github.io/fastapi-users/configuration/models/"];
   userupdatemodel[label="UserUpdate" shape=rect URL="https://fastapi-users.github.io/fastapi-users/configuration/models/"];
   userdbmodel[label="UserDB" shape=rect URL="https://fastapi-users.github.io/fastapi-users/configuration/models/"];
   usertablemodel[label="UserTable" shape=rect URL="https://fastapi-users.github.io/fastapi-users/configuration/databases/sqlalchemy/"];
   usermanagermodel[label="UserManager" shape=rect URL="https://fastapi-users.github.io/fastapi-users/configuration/user-manager/"];

   userdbfunc[label="create_user_db_func" shape=rect style=rounded URL=""];
   usermanagerfunc[label="create_user_manager_func" shape=rect style=rounded URL=""];

   jwtauth[label="JWTAuthentication" shape=rect URL="https://fastapi-users.github.io/fastapi-users/configuration/authentication/jwt/"];
   cookieauth[label="CookieAuthentication" shape=rect URL="https://fastapi-users.github.io/fastapi-users/configuration/authentication/cookie/"];

   baseapi[label="msdss-base-api" URL="https://rrwen.github.io/msdss-base-api/" style=filled];
   basedb[label="msdss-base-database" URL="https://rrwen.github.io/msdss-base-database/" style=filled];
   databases[label="databases" URL="https://pypi.org/project/databases/" style=filled];
   fastapiusers[label="FastAPI Users" URL="https://fastapi-users.github.io/fastapi-users/" style=filled];

   subgraph cluster0 {
      label=< <B>msdss_users_api.core.UsersAPI</B> >;

      style=rounded;

      subgraph cluster1 {
         label=< <B>msdss_users_api.tools</B> >;
         userdbfunc -> usermanagerfunc;
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
      userdbmodel -> fastapiusers[lhead=cluster2 ltail=cluster2];
      
      subgraph cluster3 {
          label=< <B>fastapi_users.authentication</B> >;
         jwtauth;
         cookieauth;
      }
      cookieauth -> fastapiusers[lhead=cluster3 ltail=cluster3];

      fastapiusers -> baseapi;
   }