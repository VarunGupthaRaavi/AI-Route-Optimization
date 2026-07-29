"""create_business_tables

Revision ID: 2026_07_29_0002
Revises: 2026_07_29_0001
Create Date: 2026-07-29 12:47:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2026_07_29_0002'
down_revision: Union[str, None] = '2026_07_29_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Customers Table
    op.create_table(
        'customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_customers_id'), 'customers', ['id'], unique=False)
    op.create_index(op.f('ix_customers_name'), 'customers', ['name'], unique=False)
    op.create_index(op.f('ix_customers_company_name'), 'customers', ['company_name'], unique=False)
    op.create_index(op.f('ix_customers_email'), 'customers', ['email'], unique=False)

    # 2. Vehicles Table
    vehiclestatus_enum = postgresql.ENUM('AVAILABLE', 'IN_TRANSIT', 'MAINTENANCE', name='vehiclestatus', create_type=False)
    vehiclestatus_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'vehicles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('license_plate', sa.String(length=50), nullable=False),
        sa.Column('vehicle_model', sa.String(length=100), nullable=False),
        sa.Column('capacity_kg', sa.Float(), nullable=False),
        sa.Column('volume_m3', sa.Float(), nullable=False),
        sa.Column('fuel_type', sa.String(length=50), nullable=False, server_default='DIESEL'),
        sa.Column('max_range_km', sa.Float(), nullable=False, server_default='500.0'),
        sa.Column('status', sa.Enum('AVAILABLE', 'IN_TRANSIT', 'MAINTENANCE', name='vehiclestatus'), nullable=False, server_default='AVAILABLE'),
        sa.Column('current_lat', sa.Float(), nullable=True),
        sa.Column('current_lng', sa.Float(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_vehicles_id'), 'vehicles', ['id'], unique=False)
    op.create_index(op.f('ix_vehicles_license_plate'), 'vehicles', ['license_plate'], unique=True)
    op.create_index(op.f('ix_vehicles_status'), 'vehicles', ['status'], unique=False)

    # 3. Drivers Table
    driverstatus_enum = postgresql.ENUM('IDLE', 'ON_ROUTE', 'OFF_DUTY', name='driverstatus', create_type=False)
    driverstatus_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'drivers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('license_number', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('status', sa.Enum('IDLE', 'ON_ROUTE', 'OFF_DUTY', name='driverstatus'), nullable=False, server_default='IDLE'),
        sa.Column('assigned_vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('current_lat', sa.Float(), nullable=True),
        sa.Column('current_lng', sa.Float(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=False, server_default='5.0'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_drivers_id'), 'drivers', ['id'], unique=False)
    op.create_index(op.f('ix_drivers_license_number'), 'drivers', ['license_number'], unique=True)
    op.create_index(op.f('ix_drivers_status'), 'drivers', ['status'], unique=False)

    # 4. Deliveries Table
    deliverystatus_enum = postgresql.ENUM('PENDING', 'ASSIGNED', 'IN_TRANSIT', 'DELIVERED', 'FAILED', name='deliverystatus', create_type=False)
    deliverystatus_enum.create(op.get_bind(), checkfirst=True)

    deliverypriority_enum = postgresql.ENUM('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='deliverypriority', create_type=False)
    deliverypriority_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'deliveries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('tracking_number', sa.String(length=100), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pickup_address', sa.Text(), nullable=False),
        sa.Column('delivery_address', sa.Text(), nullable=False),
        sa.Column('pickup_lat', sa.Float(), nullable=False),
        sa.Column('pickup_lng', sa.Float(), nullable=False),
        sa.Column('delivery_lat', sa.Float(), nullable=False),
        sa.Column('delivery_lng', sa.Float(), nullable=False),
        sa.Column('weight_kg', sa.Float(), nullable=False),
        sa.Column('volume_m3', sa.Float(), nullable=False, server_default='0.1'),
        sa.Column('status', sa.Enum('PENDING', 'ASSIGNED', 'IN_TRANSIT', 'DELIVERED', 'FAILED', name='deliverystatus'), nullable=False, server_default='PENDING'),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='deliverypriority'), nullable=False, server_default='MEDIUM'),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_deliveries_id'), 'deliveries', ['id'], unique=False)
    op.create_index(op.f('ix_deliveries_tracking_number'), 'deliveries', ['tracking_number'], unique=True)
    op.create_index(op.f('ix_deliveries_customer_id'), 'deliveries', ['customer_id'], unique=False)
    op.create_index(op.f('ix_deliveries_status'), 'deliveries', ['status'], unique=False)
    op.create_index(op.f('ix_deliveries_priority'), 'deliveries', ['priority'], unique=False)

    # 5. Routes Table
    routestatus_enum = postgresql.ENUM('DRAFT', 'OPTIMIZED', 'IN_PROGRESS', 'COMPLETED', name='routestatus', create_type=False)
    routestatus_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'routes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('route_code', sa.String(length=100), nullable=False),
        sa.Column('driver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('drivers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'OPTIMIZED', 'IN_PROGRESS', 'COMPLETED', name='routestatus'), nullable=False, server_default='DRAFT'),
        sa.Column('total_distance_km', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('estimated_duration_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_deliveries', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_routes_id'), 'routes', ['id'], unique=False)
    op.create_index(op.f('ix_routes_route_code'), 'routes', ['route_code'], unique=True)
    op.create_index(op.f('ix_routes_driver_id'), 'routes', ['driver_id'], unique=False)
    op.create_index(op.f('ix_routes_vehicle_id'), 'routes', ['vehicle_id'], unique=False)
    op.create_index(op.f('ix_routes_status'), 'routes', ['status'], unique=False)

    # 6. RouteStops Table
    op.create_table(
        'route_stops',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('route_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('routes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('delivery_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('deliveries.id', ondelete='CASCADE'), nullable=False),
        sa.Column('stop_sequence', sa.Integer(), nullable=False),
        sa.Column('estimated_arrival', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_route_stops_id'), 'route_stops', ['id'], unique=False)
    op.create_index(op.f('ix_route_stops_route_id'), 'route_stops', ['route_id'], unique=False)
    op.create_index(op.f('ix_route_stops_delivery_id'), 'route_stops', ['delivery_id'], unique=False)

    # 7. Notifications Table
    notificationtype_enum = postgresql.ENUM('INFO', 'WARNING', 'SUCCESS', 'ALERT', name='notificationtype', create_type=False)
    notificationtype_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.Enum('INFO', 'WARNING', 'SUCCESS', 'ALERT', name='notificationtype'), nullable=False, server_default='INFO'),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)
    op.create_index(op.f('ix_notifications_is_read'), 'notifications', ['is_read'], unique=False)


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('route_stops')
    op.drop_table('routes')
    op.drop_table('deliveries')
    op.drop_table('drivers')
    op.drop_table('vehicles')
    op.drop_table('customers')
