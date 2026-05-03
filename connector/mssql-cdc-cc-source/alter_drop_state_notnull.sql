USE testdb;
GO
ALTER TABLE testdb.dbo.Employee DROP CONSTRAINT add_state;
ALTER TABLE testdb.dbo.Employee DROP COLUMN State;
GO
EXEC sys.sp_cdc_disable_table @source_schema = [dbo], @source_name = [Employee], @capture_instance = [dbo_Employee];
GO
EXEC sys.sp_cdc_enable_table @source_schema = N'dbo', @source_name = N'Employee', @role_name = N'cdc_reader', @supports_net_changes = 0, @capture_instance = [dbo_Employee];
GO
EXEC sys.sp_cdc_help_change_data_capture;
GO
INSERT INTO testdb.dbo.Employee (EmployeeID, FirstName, LastName, Addr, zipcode) VALUES (9, 'Drop', 'State', 'Main St', 99998);
INSERT INTO testdb.dbo.Employee (EmployeeID, FirstName, LastName, Addr, zipcode) VALUES (10, 'State', 'Drop', 'Main St', 77777);
GO
