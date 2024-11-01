<div>
    <h1>ETL Pipeline with localized storage</h1>
    <span>This repository is my attempt at injesting data from the weather API from OpenWeatherMap.com.</span>
</div>

<div style="margin-top:16px;margin-bottom:16px">
<span>
    This involves:
    <ul>
        <li>Pulling and converting data from the weather api into JSON.
        <li>Using airflow to schedule data pulls.
        <li>Push pulled data through a message queuing system, Kafka. Zookeeper is used for cluster management. (Kraft mode will be used in future updates)
        <li>Process data through Spark.
        <li>Store proccessed data on a NOSQL database, Cassandra.
        <li>All processes runs on individual docker containers and uses docker compose to communicate with one another.
    </il>
</span>
</div>

<div>
<span>
    Steps:
    <ol>
        <li>Create a .env file with variables:
            <ol type="a">
                <li><b>JAVA_HOME</b> - Location of your Java openjdk@11 library.
                <li><b>weather_lat</b> - Latitude of the weather location you want.
                <li><b>weather_lon</b> - Longitude of the weather location you want.
                <li><b>weather_apikey</b> - Your weather API key.
            </ol>
        <li>Create python a virtual environment .venv in your working directory and use it as your source.
        <li>Run pip install the packages in the <u>requirements.txt</u> file.
        <li>Download the latest JAR packages from the maven repository compatible with your pyspark version and place the packages in directory"./.venv/lib/{Your Python directory}/site-packages/pyspark/jars" :
            <ol type="a">
                <li><b>spark-cassandra-connector-assembly</b>
                <li><b>spark-sql-kafka</b>
                <li><b>kafka-clients</b>
                <li><b>commons-pool2</b> - Apache Commons Pool
                <li><b>spark-token-provider-kafka</b>
            </ol>
        <li>Change your environment python source to the python installed in your working directory. <i>Export</i> the environmental variable <b>AIRFLOW_HOME</b>=current working directory. Run <i>airflow db init</i> in your terminal.
        <li>Run the startupscript.sh
        <li>Wait until you can see messages being queued for processing by Spark in your terminal.
        <li>You may run command <u>docker exec -it cassandra cqlsh -u cassandra -p cassandra</u> to enter into the Cassandra docker container and then <u>select * from spark_datastream.weather;</u> to see the data injested.
    </ol>
</span>
</div>
