
def lb_join(*lines):
    return '\n'.join(lines)

address_match = lb_join(
    'MATCH (a:Address {address: {address}})<-[u:USES]-o-[r:INPUT|OUTPUT]-t<-[c:CONTAINS]-b',
    'WITH a, t, type(r) AS rel_type, sum(o.value) AS value, b')
address_period_match = lb_join(
    address_match,
    'WHERE b.timestamp > {from} AND b.timestamp < {to}')
address_stats_query = lb_join(
    address_match,
    'RETURN count(*), min(b.timestamp), max(b.timestamp)')
address_count_query = lb_join(
    address_period_match,
    'RETURN count(*)')
address_query = lb_join(
    address_period_match,
    'RETURN a.address, t.txid, rel_type, value, b.timestamp',
    'ORDER BY b.timestamp desc')
paginated_address_query = lb_join(
    address_query,
    'SKIP {skip} LIMIT {limit}')

entity_match = lb_join(
    'MATCH (e:Entity)<-[:BELONGS_TO]-a',
    'WHERE id(e) = {id}')
entity_query = lb_join(
    'MATCH (a:Address {address: {address}})-[:BELONGS_TO]->e',
    'RETURN e, id(e)')
entity_count_query = lb_join(
    entity_match,
    'RETURN count(*)')
entity_address_query = lb_join(
    entity_match,
    'OPTIONAL MATCH a-[:HAS]->i',
    'WITH e, a, collect(i) as is',
    'ORDER BY length(is) desc',
    'LIMIT {limit}',
    'RETURN a.address as address, is as identities')

identity_query = lb_join(
    'MATCH (a:Address {address: {address}})-[:HAS]->i',
    'RETURN collect({id: id(i), name: i.name, link: i.link, source: i.source})')
reverse_identity_query = lb_join(
    'MATCH (i:Identity {name: {name}})<-[:HAS]-a',
    'RETURN a.address')
identity_add_query = lb_join(
    'MATCH (a:Address {address: {address}})',
    'CREATE a-[:HAS]->(i:Identity {name: {name}, link: {link}, source: {source}})')
identity_delete_query = lb_join(
    'MATCH (i:Identity)-[r]-()',
    'WHERE id(i) = {id}',
    'DELETE i, r')

path_query = lb_join(
    'MATCH o1-[:USES]->(start:Address {address: {address1}}),',
    '  o2-[:USES]->(end:Address {address: {address2}}),',
    '  p = shortestpath(o1-[*]->o2)',
    'UNWIND nodes(p) as n',
    'OPTIONAL MATCH n-[:USES]->a',
    'RETURN n, a')