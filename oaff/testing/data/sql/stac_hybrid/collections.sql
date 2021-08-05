INSERT INTO oaff.collections (id, title, description, keywords, license, providers, extent, temporal, schema_name, table_name) VALUES
(
    'baltimore-csa'
  , 'Baltimore Community Statistical Areas 2017'
  , 'Community Statistical Areas for Baltimore, Maryland, from 2017. Used by the Baltimore Neighbourhood Health Profile report.'
  , '{"Baltimore","Health"}'
  , NULL
  , '[{"url": "https://health.baltimorecity.gov/neighborhoods/neighborhood-health-profile-reports", "name": "Baltimore City Health Department", "roles": ["processor", "producer"]}, {"url": "https://sparkgeo.com", "name": "Sparkgeo", "roles": ["processor"]}, {"url": "https://planetarycomputer.microsoft.com", "name": "Microsoft", "roles": ["host", "processor"]}]'
  , '{"spatial": {"bbox": [[-76.711405, 39.197233, -76.529674, 39.372]]}, "temporal": {"interval": [["2017-01-01T00:00:00.000000Z", "2017-12-31T23:59:59.999999Z"]]}}'
  , '[{"type": "range", "start_field": "valid_from", "end_field": "valid_to"}]'
  , 'public'
  , 'neighbourhoods'
);