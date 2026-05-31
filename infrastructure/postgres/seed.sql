-- ============================================================
-- Store Intelligence Platform — Seed Data
-- ============================================================
-- Sample data for development and testing.
-- ============================================================

-- ===========================
-- STORES
-- ===========================
INSERT INTO stores (id, store_code, name, address, city, region, timezone, latitude, longitude) VALUES
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'STORE001', 'SIP Flagship - Mumbai Central', '123 MG Road', 'Mumbai', 'West', 'Asia/Kolkata', 19.0760, 72.8777),
    ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'STORE002', 'SIP Premium - Bangalore Indiranagar', '456 100 Feet Road', 'Bangalore', 'South', 'Asia/Kolkata', 12.9716, 77.5946),
    ('c3d4e5f6-a7b8-9012-cdef-123456789012', 'STORE003', 'SIP Express - Delhi Connaught Place', '789 Block A, CP', 'Delhi', 'North', 'Asia/Kolkata', 28.6139, 77.2090)
ON CONFLICT (store_code) DO NOTHING;

-- ===========================
-- CAMERAS
-- ===========================
INSERT INTO cameras (store_id, camera_code, name, location, resolution, fps) VALUES
    -- Store 001
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'CAM01', 'Entrance Camera', 'Main Entrance', '1920x1080', 30),
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'CAM02', 'Skincare Aisle', 'Aisle 1 - Skincare', '1920x1080', 30),
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'CAM03', 'Electronics Zone', 'Aisle 2 - Electronics', '1920x1080', 30),
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'CAM04', 'Checkout Area', 'Checkout Counter', '1920x1080', 30),
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'CAM05', 'Exit Camera', 'Main Exit', '1920x1080', 30),
    -- Store 002
    ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'CAM01', 'Entrance Camera', 'Main Entrance', '1920x1080', 30),
    ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'CAM02', 'Fashion Zone', 'Aisle 1 - Fashion', '1920x1080', 30),
    ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'CAM03', 'Checkout Area', 'Checkout Counter', '1920x1080', 30),
    -- Store 003
    ('c3d4e5f6-a7b8-9012-cdef-123456789012', 'CAM01', 'Entrance Camera', 'Main Entrance', '1920x1080', 30),
    ('c3d4e5f6-a7b8-9012-cdef-123456789012', 'CAM02', 'General Area', 'Main Floor', '1920x1080', 30),
    ('c3d4e5f6-a7b8-9012-cdef-123456789012', 'CAM03', 'Checkout Area', 'Checkout Counter', '1920x1080', 30)
ON CONFLICT (store_id, camera_code) DO NOTHING;

-- ===========================
-- ZONES
-- ===========================
INSERT INTO zones (store_id, zone_code, name, zone_type, polygon) VALUES
    -- Store 001
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'ENTRANCE', 'Main Entrance', 'entrance',
        '{"points": [[0, 0], [200, 0], [200, 150], [0, 150]]}'),
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'SKINCARE', 'Skincare Section', 'aisle',
        '{"points": [[200, 0], [500, 0], [500, 300], [200, 300]]}'),
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'ELECTRONICS', 'Electronics Section', 'aisle',
        '{"points": [[500, 0], [800, 0], [800, 300], [500, 300]]}'),
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'GROCERIES', 'Grocery Section', 'aisle',
        '{"points": [[0, 300], [400, 300], [400, 600], [0, 600]]}'),
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'CHECKOUT', 'Checkout Counter', 'checkout',
        '{"points": [[400, 300], [800, 300], [800, 450], [400, 450]]}'),
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'EXIT', 'Main Exit', 'entrance',
        '{"points": [[600, 450], [800, 450], [800, 600], [600, 600]]}'),
    -- Store 002
    ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'ENTRANCE', 'Main Entrance', 'entrance',
        '{"points": [[0, 0], [200, 0], [200, 150], [0, 150]]}'),
    ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'FASHION', 'Fashion Zone', 'aisle',
        '{"points": [[200, 0], [600, 0], [600, 300], [200, 300]]}'),
    ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'CHECKOUT', 'Checkout Counter', 'checkout',
        '{"points": [[0, 300], [600, 300], [600, 450], [0, 450]]}'),
    -- Store 003
    ('c3d4e5f6-a7b8-9012-cdef-123456789012', 'ENTRANCE', 'Main Entrance', 'entrance',
        '{"points": [[0, 0], [150, 0], [150, 100], [0, 100]]}'),
    ('c3d4e5f6-a7b8-9012-cdef-123456789012', 'GENERAL', 'General Area', 'aisle',
        '{"points": [[150, 0], [500, 0], [500, 300], [150, 300]]}'),
    ('c3d4e5f6-a7b8-9012-cdef-123456789012', 'CHECKOUT', 'Checkout Counter', 'checkout',
        '{"points": [[0, 300], [500, 300], [500, 400], [0, 400]]}')
ON CONFLICT (store_id, zone_code) DO NOTHING;

-- ============================================================
-- Seed data complete
-- ============================================================
