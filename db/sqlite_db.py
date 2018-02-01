import sqlite3

queries = {
	'SELECT': 'SELECT %s FROM %s WHERE %s',
	'SELECT_ALL': 'SELECT %s FROM %s ',
	'INSERT': 'INSERT INTO %s VALUES(%s)',
	'UPDATE': 'UPDATE %s SET %s WHERE %s',
	'DELETE': 'DELETE FROM %s where %s',
	'DELETE_ALL': 'DELETE FROM %s',
	'CREATE_TABLE': 'CREATE TABLE IF NOT EXISTS %s(%s)',
	'DROP_TABLE': 'DROP TABLE %s'}


class DatabaseObject(object):
	def __init__(self, data_file):
		self.db = sqlite3.connect(data_file, check_same_thread=False)
		self.data_file = data_file

	def free(self, cursor):
		cursor.close()

	def write(self, query, values=None):
		cursor = self.db.cursor()
		print(query, values)
		if values is not None:
			cursor.execute(query, list(values))
		else:
			cursor.execute(query)
		return cursor

	def commit(self):
		self.db.commit()

	def read(self, query, values=None):
		print(query, values)
		cursor = self.db.cursor()
		if values is not None:
			cursor.execute(query, list(values))
		else:
			cursor.execute(query)
		return cursor

	def select(self, tables, *args, order_by, **kwargs):
		vals = ','.join([l for l in args])
		locs = ','.join(tables)
		conds = ' and '.join(['%s = ?' % k for k in kwargs])
		subs = [kwargs[k] for k in kwargs]
		query = queries['SELECT'] % (vals, locs, conds)
		if order_by:
			query += " ORDER BY %s DESC" % order_by

		return self.read(query, subs)

	def select_all(self, tables, *args, order_by):
		vals = ','.join([l for l in args])
		locs = ','.join(tables)
		query = queries['SELECT_ALL'] % (vals, locs)
		if order_by:
			query += " ORDER BY %s DESC"
		return self.read(query)

	def insert(self, table_name, *args):
		values = ','.join(['?' for l in args])
		query = queries['INSERT'] % (table_name, values)
		return self.write(query, args)

	def update(self, table_name, set_args, **kwargs):
		updates = ','.join(['%s=?' % k for k in set_args])
		conds = ' and '.join(['%s like ?' % k for k in kwargs])
		vals = [set_args[k] for k in set_args]
		subs = [kwargs[k] for k in kwargs]
		query = queries['UPDATE'] % (table_name, updates, conds)
		return self.write(query, vals + subs)

	def delete(self, table_name, **kwargs):
		conds = ' and '.join(['%s=?' % k for k in kwargs])
		subs = [kwargs[k] for k in kwargs]
		query = queries['DELETE'] % (table_name, conds)
		return self.write(query, subs)

	def delete_all(self, table_name):
		query = queries['DELETE_ALL'] % table_name
		return self.write(query)

	def create_table(self, table_name, values):
		query = queries['CREATE_TABLE'] % (table_name, ','.join(values))
		self.free(self.write(query))

	def drop_table(self, table_name):
		query = queries['DROP_TABLE'] % table_name
		self.free(self.write(query))

	def disconnect(self):
		self.db.close()


class Table(DatabaseObject):
	def __init__(self, data_file, table_name, values):
		super(Table, self).__init__(data_file)
		self.create_table(table_name, values)
		self.table_name = table_name

	def select(self, *args, order_by, **kwargs):
		return super(Table, self).select([self.table_name], *args, order_by=order_by, **kwargs)

	def select_all(self, *args, order_by):
		return super(Table, self).select_all([self.table_name], *args, order_by=order_by)

	def insert(self, *args):
		return super(Table, self).insert(self.table_name, *args)

	def update(self, set_args, **kwargs):
		return super(Table, self).update(self.table_name, set_args, **kwargs)

	def delete(self, **kwargs):
		return super(Table, self).delete(self.table_name, **kwargs)

	def delete_all(self):
		return super(Table, self).delete_all(self.table_name)

	def drop(self):
		return super(Table, self).drop_table(self.table_name)

	def commit(self):
		return super(Table, self).commit()

