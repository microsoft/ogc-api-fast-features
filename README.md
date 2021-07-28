# ogc-api-fast-features

OGC Features API implementation built in Python using [FastAPI](https://fastapi.tiangolo.com/), compliant with [OGC API - Features - Part 1: Core](http://docs.opengeospatial.org/is/17-069r3/17-069r3.html), and inspired by [pygeoapi](https://pygeoapi.io/).

feapi currently supports a single data source type - PostgreSQL/PostGIS - with wider support for additional data sources planned for a future release.

# PostgreSQL/PostGIS <a id="postgresql-overview"></a>
During startup feapi interrogates one or more PostGIS connections to discover all compatible tables and derives metadata for those tables. Tables can be explicitly included or excluded during this process but by default all tables with exactly one spatial column (GEOMETRY or GEOGRAPHY type) and exactly one Primary Key column are made available.

Derived metadata for discovered tables can optionally be overridden or extended via configuration.

Multiple PostgreSQL/PostGIS data sources are supported under a single deployment and all available collections will be aggregated into a unified list.

# Demo
For a simple demo clone this repo and execute `scripts/server && scripts/demo_data`. This creates a Docker Compose stack and loads some demo data to demonstrate functionality. View at http://localhost:8008

# Non-Demo
This section describes configuration requirements for serving data from a non-demo data source.

## Environment Variable Prefix
feapi is designed in two parts: an API interface responsible for receiving requests and returning responses ("frontend"), and a business logic component ("backend"). Each has requirements and defaults regarding environment variables.

By default all API environment variables must be prefixed with "API_", e.g. `API_LOG_LEVEL`, and all business logic environment variables must be prefixed with "APP_", e.g. `APP_DATA_SOURCE_TYPES`, however the prefixes are themselves configurable via envrionment variables. Prefixing is intended to avoid any naming collisions, in which other software in the same environment requires an environment variable of the same name but with a different value. To change the default prefix set `API_ENV_VAR_PREFIX` or `APP_ENV_VAR_PREFIX`. For example, if `APP_ENV_VAR_PREFIX=ABC_` then `ABC_DATA_SOURCE_TYPES`. All references to environment variables within this document assume the default prefix.

## Data Source Types
`APP_DATA_SOURCE_TYPES` is a comma-separated list of the data source types that should be read by a feapi deployment. As only PostgreSQL/PostGIS is currently supported this must be set as `APP_DATA_SOURCE_TYPES=postgresql`

### PostgreSQL/PostGIS

#### Data Source Naming
feapi supports multiple PostgreSQL/PostGIS data sources within the same API instance and this is managed with source naming. If only using a single data source, naming is not necessary and the following environment variables may be configured:
* `APP_POSTGRESQL_PROFILE` (mandatory, must be set to `stac_hybrid`, see [below](#profiles) for details)
* `APP_POSTGRESQL_HOST` (optional, defaults to "localhost")
* `APP_POSTGRESQL_PORT` (optional, defaults to "5432")
* `APP_POSTGRESQL_USER` (optional, defaults to "postgres")
* `APP_POSTGRESQL_PASSWORD` (optional, defaults to "postgres")
* `APP_POSTGERSQL_DBNAME` (optional, defaults to "postgres")

If using multiple data sources, provide unique names in a comma-separated list e.g. `APP_POSTGRESQL_SOURCE_NAMES=name1,name2` and append each name to relevant environment variables. For example:
* `APP_POSTGRESQL_HOST_name1` (optional, defaults to "localhost")
* `APP_POSTGRESQL_HOST_name2` (optional, defaults to "localhost")
* `...` etc

Hereafter, references to environment variables that can be suffixed with a data source's name will be presented in the format `APP_ENV_VAR_NAME[_name]` to indicate that the name suffix is optional.

#### Profiles <a id="profiles"></a>
The PostgreSQL/PostGIS data source supports the concept of data source profiles, intended to support different strategies for identifying source data within a database. Only a single profile `stac_hybrid` currently exists and the profile capability may be considered over-engineering. There are currently no plans to add further profiles. At this time the environment variable `APP_POSTGRESQL_PROFILE[_name]` must be set to `stac_hybrid`.

#### MAC (Manage as Collections)
By default a PostgreSQL/PostGIS data source is expected to support a schema called "feapi" and a table within that schema called "collections". Alembic migrations run on API start to create that schema and table if they do not already exist. Some users may not want feapi to modify their database, or may not want to configure feapi with a database user account that has the necessary privileges. The expectation of `feapi.collections` existing, and the Alembic functionality to create it, can be disabled by setting `APP_POSTGRESQL_MAC[_name]=0`. With `MAC` disabled you will not be able to override or extend derived metadata (see [below](#metadata-table)).

If you have reservations around configuring feapi with a database user account that has elevated privileges you can simply start the container once using a privileged account, let it upgrade the database to its expected version, and thereafter run feapi using a non-privileged account. Write access is only needed when a new release includes schema changes and this is not expected to happen on a regular basis.

#### Temporal Fields <a id="temporal-fields"></a>
During data interrogation (see [above](#postgresql-overview)) feapi identifies temporal fields in supported tables and derives metadata to support temporal filtering in data requests. TIMESTAMP WITH TIME ZONE, TIMESTAMP WITHOUT TIME ZONE, and DATE types are supported. Each temporal field is identified individually, and is therefore assumed to represent a single point in time, and this influences how temporal data requests are handled. If an API caller provides a temporal range each temporal field is evaluated on whether its single point in time falls within that range. If an API caller provides a single point in time each temporal field is evaluated on whether it equals that moment.

Sometimes multiple temporal fields in a table may actually represent the beginning and end of a time range, and this affects how a temporal data request should be evaluated. If an API caller provides a temporal range each range within the data should be evaluated by intersection, and if the API caller provides a single point in time each range within the data should be evaluated on whether it contains that moment.

If a table contains temporal ranges it must be configured via `feapi.collections` to indicate a relationship between temporal fields. See [below](#metadata-table) for details.

##### Default Time Zone
If temporal data is stored as TIMESTAMP WITH TIME ZONE PostgreSQL stores data in UTC and transparently converts to any time zone requested by an API caller. However, data stored as TIMESTAMP WITHOUT TIME ZONE or DATE does not have an associated time zone and both the database and feapi are ignorant to its intended context. It is not possible in Python (nor wise in general) to compare temporal data in UTC - as provided by API callers issuing temporal data requests - with temporal data that is not time zone aware. Temporal data must be associated with a time zone, so feapi assigns a default. The default can be configured via `APP_POSTGRESQL_DEFAULT_TZ[_name]` and defaults to "UTC". This value must be a string compatible with pytz. Execute `pip install pytz && python -c "import os; import pytz; print(os.linesep.join(pytz.all_timezones))"` to see available time zones in pytz.

##### Supported Temporal Types <a id="temporal-types"></a>
In addition to TIMESTAMP WITH TIME ZONE, TIMESTAMP WITHOUT TIME ZONE, and DATE, PostgreSQL also supports a number of range-like temporal data types. These types are not currently supported but support may be added at a later date.

#### Metadata and `feapi.collections` <a id="metadata-table"></a>
Derived metadata on any supported table can be overridden with an entry in `feapi.collections`
| Column | Nullable | Purpose | Example |
|--------|----------|---------|---------|
| id | False | Overrides the generated collection ID. Generated IDs are stable SHA-256 hashes generated from some source parameters | 'unique-collection-id' |
| title | False | Overrides table name as default collection title | 'Unique Collection Title' |
| description | True | Overrides empty description field, which cannot be derived during data interrogation | 'I provide descriptive prose about this dataset' |
| keywords | True | Provides zero or more keywords for collection tagging in support of SEO and possible future functionality (PostgreSQL array format, not JSON/JSONB) | '{"keyword 1","keyword 2"}' |
| license | True | Provides any licensing conditions attached to the collection | 'Example license text' |
| providers | True | Provides information about zero or more entities associated with the collection, e.g. who created it, who processed it, etc. JSON format, where "url" and "name" properties are mandatory but "roles" property is optional | '[{"url": "https://domain/path", "name": "Data provider name", "roles": ["producer", "maintainer"]}]' |
| extent | True | Overrides derived spatial and/or temporal extents. JSON format. Schema matches [STAC spec's extent schema](https://github.com/radiantearth/stac-spec/blob/master/collection-spec/collection-spec.md#extent-object) except "spatial" and "temporal" properties are optional and omitting either will retain that part of the derived extent | '{"spatial": {"bbox": [[-1, -1, 1, 1]]}, "temporal": {"interval": [["1955-11-05T01:35:00Z", "1985-10-26T01:36:00Z"]]}}' |
| temporal | True | Overrides derived temporal column definitions, optionally linking two temporal columns into a range. See [above](#temporal-fields) for details. JSON format, supporting two "types" | '[{"type": "range", "start_field": "starts_at", "end_field": "ends_at"}, {"type": "instant", "field": "created"}]' |
| schema_name | False | References the schema containing the table | 'public' |
| table_name | False | References the table | 'great_scott' |

#### Whitelisting/Blacklisting
During data interrogation feapi will identify all tables that can be served via its API interface. This may not always be desirable, for example if the database contains a mix of sensitive and non-sensitive data. Whitelisting permits an explicit list of tables to be exposed and blacklisting prevents an explicit list of tables from being exposed. Whitelist and blacklist are exclusive; if both are provided, both will be ignored. Whitelisted or blacklisted table names must be fully-qualified - i.e. `schema_name.table_name` - and multiple tables can be specified in a comma-separated list, e.g.
* `APP_POSTGRESQL_LAYER_WHITELIST[_name]=public.table1,public.table2`
* `APP_POSTGRESQL_LAYER_BLACKLIST[_name]=public.table1,public.table2`

## CITE Compliance
Follow the instructions [here](https://cite.opengeospatial.org/teamengine/) to execute CITE compliance tests against feapi. If executing tests in a Docker container against an API instance in a separate Docker container you may need to reference a special hostname. For example, to execute using Docker on MacOS:
* `scripts/server && scripts/demo_data` to start the API containers
* `docker run --rm -p 8081:8080 ogccite/ets-ogcapi-features10` to start the CITE testing container
* Navigate browser to http://localhost:8081
* Login with `ogctest/ogctest`
* Start a new test session
* Provide http://docker.for.mac.localhost:8008 for the test URL
    * Note the lack of a trailing slash. There appears to be an error in the CITE tests that results in invalid request paths (e.g. `///conformance`) if the test URL ends in a trailing slash

# Developing
The following provides information for developers looking to maintain or extend feapi. Development requires Python 3.8+

## Commands
- `scripts/setup`: configure local dev env (Python virtual env recommended)
- `scripts/server`: build and start API containers
- `scripts/demo_data`: load test/demo data for development and refresh API configuration
- `scripts/stop`: stop API containers
- `scripts/update`: rebuild containers
- `scripts/test`: execute tests
- `scripts/cibuild`: execute same build & test process as CI build (executes tests, no Docker build cache)
- `scripts/console`: enter console for named container
- `scripts/logs`: follow logs for named container
- `scripts/update_i18n`: extract and compile translations using Babel
- `scripts/format`: format code using isort and Black
- `scripts/debug_test_start`: start a test database instance to support debugging tests (see [below](#test-debug))
- `scripts/debug_test_stop`: stop test database instance

## Architecture

### FastAPI
feapi's frontend uses FastAPI but the backend is not tightly-coupled to that framework. Frontend routers interpret path and query parameters and build request objects using request classes defined in the backend. A single `delegate` method passes request objects to the backend and awaits a response. Responses provide either data or error detail and an appropriate API response is constructed from whichever is returned. During the frontend's startup sequence a `FrontendConfiguration` object is passed to the backend, providing key frontend properties that need to be known by the backend. Examples:
1. when the backend builds a data response to an API request it needs to know the root path from which the API is served to correctly build any links in the response
2. when the backend renders an HTML-templated response it needs to know the hosted location of JavaScript and CSS assets

The backend should have no knowledge of frontend behaviour, including request parameter names, beyond what is explicitly provided via `FrontendConfiguration`.

Thanks in part to FastAPI's use of async feapi is end-to-end async when responding to API calls, including async connections to PostgreSQL/PostGIS. This should improve its ability to support higher concurrent loads, but benchmarking is required to establish a quantitaive baseline and comparison with other OGC API - Features implementations.

## Pygeofilter
feapi depends on [pygeofilter](https://github.com/geopython/pygeofilter) to translate spatial and temporal data request parameters into an abstract query structure, and then from that abstract structure into PostgreSQL-compatible SqlAlchemy query objects. In Part 1 (Core) of the OGC API - Features specification only basic spatial and temporal filters are required, and pygeofilter is able to support those requirements. pygeofilter also has developing support for Simple CQL as described in [OGC API - Features - Part 3: Filtering and the Common Query Language (CQL)](https://portal.ogc.org/files/96288) and when feapi extends to CQL support pygeofilter is expected to provide much of that functionality.

## Data Sources
During startup the data interrogation phase creates an object whose class extends the `DataSource` base class for each of the configured data sources. Each `DataSource` is required to implement a number of methods including `get_layers`. In order to support additional data source types new `DataSource` sub-classes will be required.

## Re/configuration

Layer objects represent the layers discovered during the data interrogation phase and are stored in memory. If data sources are modified, or environment variables that affect data interrogation are modified, interrogation must be re-run to acknowledge those changes. 

The simplest way to re-run data interrogation is to restart the application, however this may not always be desirable. The frontend provides an endpoint `POST /control/reconfigure` that is only accessible from certain request origins and origins are configurable via an environment variable. In theory an administrator could give themselves - or a machine acting on their behalf - access to this endpoint and initiate a reconfiguration following data changes, though this strategy has not been explored extensively. Attempts to access `POST /control/reconfigure` from a non-permitted origin will result in a 404 response.

## Feature [Set] Provider
feapi currently supports HTML and JSON/GeoJSON output encodings for metadata (e.g. `/collections`) and data (e.g. `/collections/{collection_id}/items`) requests. Future development efforts are expected to add additional output encodings such as GeoPackage or FlatGeoBuf.

Given the goal of supporting multiple data source types, and multiple output encoding formats, one possible strategy is to use a dependency such as GDAL OGR for data handling. Data can be translated from a wide range of source formats to OGR Layer/Feature objects and from those objects to a wide range of output formats. However there are several scenarios where such a translation will be inefficient. For example, data requested from a GeoJSON source format in a GeoJSON output encoding should not need to be translated via OGR as this unnecessary translation could add considerable overhead to the user's request. Similarly, some source formats may provide the ability to generate a data response in a range of output encodings and thereby offer a more efficient approach to data retrieval. Finally, for many output formats OGR requires a file path to which it can write data. Writing data to disk, and then reading it back to populate the API response, could add considerable overhead to request processing times.

The `FeatureProvider` and `FeatureSetProvider` base classes support the ability of the API to acknowledge, and take advantage of, nuances in the relationships between source and target formats. `PostgresqlFeatureProvider` and `PostgresqlFeatureSetProvider` utilise PostgreSQL/PostGIS's ability to generate results in GeoJSON format and thereby avoid the need for object marshalling and JSON serialization within the API.

As additional support is added for other source formats and output encodings it may be necessary to marshall from a source format into a common format using the OGR API, however that does not warrant a common marshalling strategy across all output encodings and any inefficiencies should be limited to those source/output pairs that require marshalling.

## Debugging
### Debug API in Visual Studio Code
The following launch.json config can be used to debug the API (http://localhost:8123).
A database instance must be running on localhost:5432.
Execute `docker-compose up -d postgres` to establish a database instance if one is not already running. Run `scripts/demo_data` to create data if required.
A debug instance of the API can execute alongside a running instance of the main Docker Compose stack.
```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI",
            "type": "python",
            "request": "launch",
            "module": "feapi.fastapi.api.main",
            "cwd": "${workspaceFolder}",
            "console": "integratedTerminal",
            "justMyCode": false,
            "args":[ "8123" ],
            "env": {
                "API_LOG_LEVEL": "debug",
                "APP_DATA_SOURCE_TYPES": "postgresql",
                "APP_POSTGRESQL_SOURCE_NAMES": "stac",
                "APP_POSTGRESQL_PROFILE_stac": "stac_hybrid"
            }
        }
    ]
}
```
### Debug Tests in Visual Studio Code <a id="test-debug"></a>
The following launch.json config can be used to debug tests. A database instance must be running on localhost:2345.
Execute `scripts/debug_test_start` to establish a test database instance.
Remove the test database instance with `scripts/debug_test_stop`.
To debug a single test add `, "-k", "<<test name>>"` to the `args` array.
The test database instance and tests can execute alongside a running instance of the main Docker Compose stack.
```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["feapi", "--maxfail=1"],
            "env": {
                "APP_DATA_SOURCE_TYPES": "postgresql",
                "APP_POSTGRESQL_SOURCE_NAMES": "stac",
                "APP_POSTGRESQL_HOST_stac": "localhost",
                "APP_POSTGRESQL_PROFILE_stac": "stac_hybrid",
                "APP_POSTGRESQL_PORT_stac": "2345"
            }
        }
    ]
}
```

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

# Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
