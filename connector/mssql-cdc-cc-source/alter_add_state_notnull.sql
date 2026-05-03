USE testdb;
GO
ALTER TABLE testdb.dbo.Employee add State NVARCHAR(50) NOT NULL CONSTRAINT add_state DEFAULT 'AB';
GO
EXEC sys.sp_cdc_disable_table @source_schema = [dbo], @source_name = [Employee], @capture_instance = [dbo_Employee];
GO
EXEC sys.sp_cdc_enable_table @source_schema = N'dbo', @source_name = N'Employee', @role_name = N'cdc_reader', @supports_net_changes = 0, @capture_instance = [dbo_Employee];
GO
EXEC sys.sp_cdc_help_change_data_capture;
GO
INSERT INTO testdb.dbo.Employee (EmployeeID, FirstName, LastName, Addr, State) VALUES (5, 'Add', 'State', 'Main St', 'FL');
INSERT INTO testdb.dbo.Employee (EmployeeID, FirstName, LastName, Addr, State) VALUES (6, 'State', 'Add', 'Wall St', 'CA');
