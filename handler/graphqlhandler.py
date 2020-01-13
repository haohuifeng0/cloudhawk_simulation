# -*- coding: utf-8 -*-
import logging

import graphene
import jsonschema
import simplejson

import tornado.web
from graphql import GraphQLError
from graphql.error import GraphQLSyntaxError, GraphQLLocatedError
from jsonschema import Draft4Validator, FormatChecker, ValidationError
from simplejson import dumps as json_encode
from simplejson import loads as json_decode
from tornado import httputil

from handler.schemahandler import Query, Mutation
from libs import RESPONSE, schemas
from libs.RESPONSE import AppError


def dump_error(err):
    if isinstance(err, GraphQLSyntaxError):
        return {
            'status': RESPONSE.ILLEGAL_FORMAT,
            'message': err.message,
        }

    if isinstance(err, GraphQLLocatedError):
        err = err.original_error

    if isinstance(err, AppError):
        e = {
            'status': err.app_status_code,
            'message': err.reason,
        }
        if err.data:
            e['verbose'] = err.data
        return e
    elif isinstance(err, GraphQLError):
        return {
            'status': RESPONSE.ILLEGAL_FORMAT,
            'message': err.message,
        }
    elif isinstance(err, tornado.web.HTTPError):
        return {
            'status': err.status_code,
            'message': httputil.responses.get(err.status_code, 'Unknown error.'),
            'verbose': 'http error',
        }
    else:
        return {
            'status': RESPONSE.SERVER_ERROR,
            'message': 'Server error.',
            'verbose': str(err),
        }


class GraphiQLHandler(tornado.web.RequestHandler):

    graphiql_html = """<!--
     *  Copyright (c) Facebook, Inc.
     *  All rights reserved.
     *
     *  This source code is licensed under the license found in the
     *  LICENSE file in the root directory of this source tree.
    -->
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          body {
            height: 100%;
            margin: 0;
            width: 100%;
            overflow: hidden;
          }
          #graphiql {
            height: 100vh;
          }
        </style>

        <!--
          This GraphiQL example depends on Promise and fetch, which are available in
          modern browsers, but can be "polyfilled" for older browsers.
          GraphiQL itself depends on React DOM.
          If you do not want to rely on a CDN, you can host these files locally or
          include them directly in your favored resource bunder.
        -->
        <script src="//cdn.jsdelivr.net/es6-promise/4.0.5/es6-promise.auto.min.js"></script>
        <script src="//cdn.jsdelivr.net/fetch/0.9.0/fetch.min.js"></script>
        <script src="//cdn.jsdelivr.net/react/15.4.2/react.min.js"></script>
        <script src="//cdn.jsdelivr.net/react/15.4.2/react-dom.min.js"></script>

        <!--
          These two files can be found in the npm module, however you may wish to
          copy them directly into your environment, or perhaps include them in your
          favored resource bundler.
         -->
        <script src="//cdn.jsdelivr.net/npm/graphiql@0.11.11/graphiql.min.js"></script>
        <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/graphiql@0.11.11/graphiql.css" />

      </head>
      <body>
        <div id="graphiql">Loading...</div>
        <script>

          /**
           * This GraphiQL example illustrates how to use some of GraphiQL's props
           * in order to enable reading and updating the URL parameters, making
           * link sharing of queries a little bit easier.
           *
           * This is only one example of this kind of feature, GraphiQL exposes
           * various React params to enable interesting integrations.
           */

          // Parse the search string to get url parameters.
          var search = window.location.search;
          var parameters = Object();
          search.substr(1).split('&').forEach(function (entry) {
            var eq = entry.indexOf('=');
            if (eq >= 0) {
              parameters[decodeURIComponent(entry.slice(0, eq))] =
                decodeURIComponent(entry.slice(eq + 1));
            }
          });

          // if variables was provided, try to format it.
          if (parameters.variables) {
            try {
              parameters.variables =
                JSON.stringify(JSON.parse(parameters.variables), null, 2);
            } catch (e) {
              // Do nothing, we want to display the invalid JSON as a string, rather
              // than present an error.
            }
          }

          // When the query and variables string is edited, update the URL bar so
          // that it can be easily shared
          function onEditQuery(newQuery) {
            parameters.query = newQuery;
            updateURL();
          }

          function onEditVariables(newVariables) {
            parameters.variables = newVariables;
            updateURL();
          }

          function onEditOperationName(newOperationName) {
            parameters.operationName = newOperationName;
            updateURL();
          }

          function updateURL() {
            var newSearch = '?' + Object.keys(parameters).filter(function (key) {
              return Boolean(parameters[key]);
            }).map(function (key) {
              return encodeURIComponent(key) + '=' +
                encodeURIComponent(parameters[key]);
            }).join('&');
            history.replaceState(null, null, newSearch);
          }

          // Defines a GraphQL fetcher using the fetch API. You're not required to
          // use fetch, and could instead implement graphQLFetcher however you like,
          // as long as it returns a Promise or Observable.
          function graphQLFetcher(graphQLParams) {
            // This example expects a GraphQL server at the path /graphql.
            // Change this to point wherever you host your GraphQL server.
            return fetch('#MOUNT_POINT#', {
              method: 'post',
              headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(graphQLParams),
              credentials: 'include',
            }).then(function (response) {
              return response.text();
            }).then(function (responseBody) {
              try {
                return JSON.parse(responseBody);
              } catch (error) {
                return responseBody;
              }
            });
          }

          // Render <GraphiQL /> into the body.
          // See the README in the top level of this module to learn more about
          // how you can customize GraphiQL by providing different values or
          // additional child elements.
          ReactDOM.render(
            React.createElement(GraphiQL, {
              fetcher: graphQLFetcher,
              query: parameters.query,
              variables: parameters.variables,
              operationName: parameters.operationName,
              onEditQuery: onEditQuery,
              onEditVariables: onEditVariables,
              onEditOperationName: onEditOperationName
            }),
            document.getElementById('graphiql')
          );
        </script>
      </body>
    </html>
    """

    def initialize(self, endpoint):
        self.graphiql_html = """<!--
     *  Copyright (c) Facebook, Inc.
     *  All rights reserved.
     *
     *  This source code is licensed under the license found in the
     *  LICENSE file in the root directory of this source tree.
    -->
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          body {
            height: 100%;
            margin: 0;
            width: 100%;
            overflow: hidden;
          }
          #graphiql {
            height: 100vh;
          }
        </style>

        <!--
          This GraphiQL example depends on Promise and fetch, which are available in
          modern browsers, but can be "polyfilled" for older browsers.
          GraphiQL itself depends on React DOM.
          If you do not want to rely on a CDN, you can host these files locally or
          include them directly in your favored resource bunder.
        -->
        <script src="//cdn.jsdelivr.net/es6-promise/4.0.5/es6-promise.auto.min.js"></script>
        <script src="//cdn.jsdelivr.net/fetch/0.9.0/fetch.min.js"></script>
        <script src="//cdn.jsdelivr.net/react/15.4.2/react.min.js"></script>
        <script src="//cdn.jsdelivr.net/react/15.4.2/react-dom.min.js"></script>

        <!--
          These two files can be found in the npm module, however you may wish to
          copy them directly into your environment, or perhaps include them in your
          favored resource bundler.
         -->
        <script src="//cdn.jsdelivr.net/npm/graphiql@0.11.11/graphiql.min.js"></script>
        <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/graphiql@0.11.11/graphiql.css" />

      </head>
      <body>
        <div id="graphiql">Loading...</div>
        <script>

          /**
           * This GraphiQL example illustrates how to use some of GraphiQL's props
           * in order to enable reading and updating the URL parameters, making
           * link sharing of queries a little bit easier.
           *
           * This is only one example of this kind of feature, GraphiQL exposes
           * various React params to enable interesting integrations.
           */

          // Parse the search string to get url parameters.
          var search = window.location.search;
          var parameters = Object();
          search.substr(1).split('&').forEach(function (entry) {
            var eq = entry.indexOf('=');
            if (eq >= 0) {
              parameters[decodeURIComponent(entry.slice(0, eq))] =
                decodeURIComponent(entry.slice(eq + 1));
            }
          });

          // if variables was provided, try to format it.
          if (parameters.variables) {
            try {
              parameters.variables =
                JSON.stringify(JSON.parse(parameters.variables), null, 2);
            } catch (e) {
              // Do nothing, we want to display the invalid JSON as a string, rather
              // than present an error.
            }
          }

          // When the query and variables string is edited, update the URL bar so
          // that it can be easily shared
          function onEditQuery(newQuery) {
            parameters.query = newQuery;
            updateURL();
          }

          function onEditVariables(newVariables) {
            parameters.variables = newVariables;
            updateURL();
          }

          function onEditOperationName(newOperationName) {
            parameters.operationName = newOperationName;
            updateURL();
          }

          function updateURL() {
            var newSearch = '?' + Object.keys(parameters).filter(function (key) {
              return Boolean(parameters[key]);
            }).map(function (key) {
              return encodeURIComponent(key) + '=' +
                encodeURIComponent(parameters[key]);
            }).join('&');
            history.replaceState(null, null, newSearch);
          }

          // Defines a GraphQL fetcher using the fetch API. You're not required to
          // use fetch, and could instead implement graphQLFetcher however you like,
          // as long as it returns a Promise or Observable.
          function graphQLFetcher(graphQLParams) {
            // This example expects a GraphQL server at the path /graphql.
            // Change this to point wherever you host your GraphQL server.
            return fetch('#MOUNT_POINT#', {
              method: 'post',
              headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(graphQLParams),
              credentials: 'include',
            }).then(function (response) {
              return response.text();
            }).then(function (responseBody) {
              try {
                return JSON.parse(responseBody);
              } catch (error) {
                return responseBody;
              }
            });
          }

          // Render <GraphiQL /> into the body.
          // See the README in the top level of this module to learn more about
          // how you can customize GraphiQL by providing different values or
          // additional child elements.
          ReactDOM.render(
            React.createElement(GraphiQL, {
              fetcher: graphQLFetcher,
              query: parameters.query,
              variables: parameters.variables,
              operationName: parameters.operationName,
              onEditQuery: onEditQuery,
              onEditVariables: onEditVariables,
              onEditOperationName: onEditOperationName
            }),
            document.getElementById('graphiql')
          );
        </script>
      </body>
    </html>
    """.replace('#MOUNT_POINT#', endpoint)

    def get(self):
        self.write(self.graphiql_html)


class GQHandler(tornado.web.RequestHandler):

    validator = Draft4Validator({
        'type': 'object',
        'properties': {
            'query': schemas.types.str,
        },
        'required': ['query'],
    }, format_checker=FormatChecker())

    def write_data(self, data=None, errors=None):
        self.set_header("Content-Type", "application/json; charset=utf-8")
        if not errors:
            self.write(simplejson.dumps({
                'data': data,
                'errors': [],
            }))
            return

        errs = []
        for err in errors:
            errs.append(dump_error(err))

        self.write(simplejson.dumps({
            'data': data,
            'errors': errs,
        }))

    def write_error(self, status_code, **kwargs):
        self.set_header("Content-Type", "application/json; charset=utf-8")
        err = None
        if 'exc_info' in kwargs:
            exc = kwargs['exc_info'][1]
            if isinstance(exc, AppError):
                err = {
                    'status': exc.app_status_code,
                    'message': exc.reason,
                }
                if exc.data:
                    err['verbose'] = exc.data
            elif isinstance(exc, tornado.web.HTTPError):
                err = {
                    'status': status_code,
                    'message': self._reason,
                }
        if not err:
            err = {
                'status': status_code,
                'message': self._reason,
            }

        self.write(simplejson.dumps({
            'data': None,
            'errors': [err]
        }))

    def _validate_args(self, validator, read_args):
        try:
            args = read_args()

            if validator is not None:
                if isinstance(validator, jsonschema.Draft4Validator) or \
                   isinstance(validator, jsonschema.Draft3Validator):
                    validator.validate(args)
                else:
                    logging.error('invalid validator: %s', validator)
                    AppError(RESPONSE.SERVER_ERROR)

            return args
        except AppError:
            raise
        except ValidationError as e:
            path = '/' + ('/'.join([str(c) for c in e.path]))
            err_msg = "{}: {}".format(path, e.message)
            logging.info("invalid request args", err_msg=err_msg)
            raise AppError(RESPONSE.ILLEGAL_FORMAT, {
                'reason': err_msg,
                'schema': e.schema,
            })
        except Exception as e:
            raise AppError(RESPONSE.ILLEGAL_FORMAT, {
                'reason': '{}'.format(e)})

    def parse_json_body(self, validator=None):
        return self._validate_args(validator,
                                   lambda: json_decode(self.request.body))

    schema = graphene.Schema(Query, Mutation)

    def post(self):
        args = self.parse_json_body(self.validator)
        query = args['query']
        op = args.get('operationName', None)
        vs = args.get('variables', None)

        compact_query = ' '.join(
            l.strip() for l in query.splitlines() if l.strip()
        )
        logging.info(compact_query + f'op:{op}, vars:{vs}')

        result = self.schema.execute(
            args['query'],
            operation_name=op,
            variable_values=vs,
        )

        self.write_data(result.data, result.errors)
