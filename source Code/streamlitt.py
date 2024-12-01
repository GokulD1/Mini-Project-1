import streamlit as st
import pymysql
import pandas as pd

def connect_to_database():
    return pymysql.connect(
        host="localhost",
        user="gokuld",
        password="Guvi",
        database="redbus",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

def fetch_bus_details():
    conn = connect_to_database()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        bd.*,
        r.route_name
    FROM 
        bus_details bd
    JOIN 
        routes r ON bd.route_id = r.route_id
    """
    
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    
    df = pd.DataFrame(data)
    
    df["departing_time_numeric"] = df["departing_time"].apply(lambda x: int(x.split(":")[0]) + int(x.split(":")[1]) / 60)
    
    return df

def get_unique_values(df, column):
    return sorted(df[column].unique().tolist())

def main():
    st.title("RedBus Data Explorer")
    df = fetch_bus_details()
    st.sidebar.header("Filters")
    routes = ["All"] + get_unique_values(df, "route_name")
    selected_route = st.sidebar.selectbox("Select Route", routes)
    bus_types = ["All"] + get_unique_values(df, "bus_type")
    selected_bus_type = st.sidebar.selectbox("Select Bus Type", bus_types)

    price_range = st.sidebar.slider(
        "Price Range (INR)",
        float(df["price"].min()),
        float(df["price"].max()),
        (float(df["price"].min()), float(df["price"].max()))
    )
    
    rating_range = st.sidebar.slider(
        "Star Rating",
        float(df["star_rating"].min()),
        float(df["star_rating"].max()),
        (float(df["star_rating"].min()), float(df["star_rating"].max()))
    )
    
    availability_range = st.sidebar.slider(
        "Seat Availability",
        int(df["seat_availability"].min()),
        int(df["seat_availability"].max()),
        (int(df["seat_availability"].min()), int(df["seat_availability"].max()))
    )

    start_time_range = st.sidebar.slider(
        "Departure Time (Hours)",
        float(df["departing_time_numeric"].min()),
        float(df["departing_time_numeric"].max()),
        (float(df["departing_time_numeric"].min()), float(df["departing_time_numeric"].max()))
    )
    
    filtered_df = df.copy()
    
    if selected_route != "All":
        filtered_df = filtered_df[filtered_df["route_name"] == selected_route]
    
    if selected_bus_type != "All":
        filtered_df = filtered_df[filtered_df["bus_type"] == selected_bus_type]
    
    filtered_df = filtered_df[
        (filtered_df["price"] >= price_range[0]) &
        (filtered_df["price"] <= price_range[1]) &
        (filtered_df["star_rating"] >= rating_range[0]) &
        (filtered_df["star_rating"] <= rating_range[1]) &
        (filtered_df["seat_availability"] >= availability_range[0]) &
        (filtered_df["seat_availability"] <= availability_range[1]) &
        (filtered_df["departing_time_numeric"] >= start_time_range[0]) &
        (filtered_df["departing_time_numeric"] <= start_time_range[1])
    ]
    
    st.header("Filtered Results")
    st.write(f"Found {len(filtered_df)} buses matching your criteria")
    
    st.dataframe(
        filtered_df[[
            "route_name", "bus_name", "bus_type", "departing_time",
            "duration", "reaching_time", "star_rating", "price",
            "seat_availability"
        ]],
        hide_index=True
    )

if __name__ == "__main__":
    main()
