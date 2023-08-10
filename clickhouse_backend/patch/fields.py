from django.db.models.fields import json

_g_old_from_db = None

def key_transform_as_clickhouse(self, compiler, connection):
    lhs, params, key_transforms = self.preprocess_lhs(compiler, connection)
    sql = lhs
    params = list(params)
    for key in key_transforms:
        if key.isdigit():
            sql = f"{sql}[%s]"
            params.append(int(key) + 1)
        else:
            sql = f"({sql}, %s)"
            params.append(key)
    return sql, tuple(params)

def patched_db_from(obj, value, expression, connection):
    try:
        return _g_old_from_db(obj, value, expression, connection)
    except UnicodeDecodeError:
        return ''

def patch_jsonfield():
    json.KeyTransform.as_clickhouse = key_transform_as_clickhouse
    global _g_old_from_db
    _g_old_from_db = json.JSONField.from_db_value
    json.JSONField.from_db_value = patched_db_from
