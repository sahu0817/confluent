USE testdb;
GO
ALTER TABLE testdb.dbo.Employee add Addr NVARCHAR(50) NOT NULL CONSTRAINT add_addr DEFAULT 'defval';
GO
EXEC sys.sp_cdc_disable_table @source_schema = [dbo], @source_name = [Employee], @capture_instance = [dbo_Employee];
GO
EXEC sys.sp_cdc_enable_table @source_schema = N'dbo', @source_name = N'Employee', @role_name = N'cdc_reader', @supports_net_changes = 0;
GO
EXEC sys.sp_cdc_help_change_data_capture;
GO
INSERT INTO testdb.dbo.Employee (EmployeeID, FirstName, LastName, Addr) VALUES (3, 'Bill', 'Board', 'Main St');
INSERT INTO testdb.dbo.Employee (EmployeeID, FirstName, LastName, Addr) VALUES (4, 'Willy', 'Wonka', 'Wall St');
