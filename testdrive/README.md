# testdrive

`testdrive` is a library for:

 * Building a URI for a test case from a base URI and the test case path
 * Generating JUnit test results for supplying to [Red Hat DCI][1] or other CI
 * Generating [Asciidoc][3] test results for human consumption

The implementation of [testdrive.run.main()][2] provides an illustration of how
this library can be used.

## testdrive.run

Module `testdrive.run` is a convenience tool for running a set of tests
specified as lines of JSON in a file. Using example files in this repo:

    $ env PYTHONPATH=src python3 -m testdrive.run https://github.com/redhat-partner-solutions/testdrive/ examples/sequence/tests.json
    {"result": false, "reason": "something went wrong", "data": {"foo": "bar"}, "argv": [], "id": "https://github.com/redhat-partner-solutions/testdrive/A/", "timestamp": "2023-08-25T07:22:57.368206+00:00", "time": 0.056209}
    {"result": true, "reason": null, "data": {"baz": 99}, "argv": [], "id": "https://github.com/redhat-partner-solutions/testdrive/B/", "timestamp": "2023-08-25T07:22:57.424912+00:00", "time": 0.058858}
    {"result": false, "reason": "no particular reason", "argv": [], "id": "https://github.com/redhat-partner-solutions/testdrive/C/", "timestamp": "2023-08-25T07:22:57.483833+00:00", "time": 0.005414}

Alternatively, tests can be supplied on stdin. In this case option `--basedir`
must be supplied. Using example files in this repo:

    $ cat examples/sequence/tests.json | env PYTHONPATH=src python3 -m testdrive.run --basedir=examples/sequence/ https://github.com/redhat-partner-solutions/testdrive/ -
    {"result": false, "reason": "something went wrong", "data": {"foo": "bar"}, "argv": [], "id": "https://github.com/redhat-partner-solutions/testdrive/A/", "timestamp": "2023-08-25T07:25:49.818848+00:00", "time": 0.029972}
    {"result": true, "reason": null, "data": {"baz": 99}, "argv": [], "id": "https://github.com/redhat-partner-solutions/testdrive/B/", "timestamp": "2023-08-25T07:25:49.848893+00:00", "time": 0.028337}
    {"result": false, "reason": "no particular reason", "argv": [], "id": "https://github.com/redhat-partner-solutions/testdrive/C/", "timestamp": "2023-08-25T07:25:49.877293+00:00", "time": 0.003946}

`testdrive.run` can also be instructed to call a script colocated with a test
implementation to plot images of input data / results. Option `--imagedir` must
be supplied to generate images. Option `--plotter` gives the name of the script
to call: if there is not a script with this name colocated with the test
implementation, then plotting is skipped for this image. Using example files in
this repo:

    $ find examples/ -name 'plot*'
    examples/sequence/B/plot.sh
    examples/sequence/C/plot.sh

(These scripts only print examples of expected JSON, they do not create images.)

    $ cat examples/sequence/tests.json | env PYTHONPATH=src python3 -mtestdrive.run --basedir=examples/sequence/ --imagedir=. --plotter=plot.sh https://github.com/redhat-partner-solutions/testdrive/ -
    {"result": false, "reason": "something went wrong", "data": {"foo": "bar"}, "argv": [], "id": "https://github.com/redhat-partner-solutions/testdrive/A/", "timestamp": "2023-09-04T15:31:30.336801+00:00", "time": 0.029548}
    {"result": true, "reason": null, "data": {"baz": 99}, "argv": [], "id": "https://github.com/redhat-partner-solutions/testdrive/B/", "timestamp": "2023-09-04T15:31:30.366548+00:00", "time": 0.090166, "plot": [{"path": "./B_testimpl.png", "title": "foo bar baz"}]}
    {"result": false, "reason": "no particular reason", "argv": [], "id": "https://github.com/redhat-partner-solutions/testdrive/C/", "timestamp": "2023-09-04T15:31:30.460420+00:00", "time": 0.003882, "plot": [{"path": "./C_test.png"}, "./C_test_lhs.pdf", {"path": "./C_test_rhs.pdf", "title": "rhs"}]}

## testdrive.junit

Module `testdrive.junit` can be used to generate JUnit test results from lines
of JSON (one line per test case result):

    $ python3 -m testdrive.run https://github.com/redhat-partner-solutions/testdrive/ examples/sequence/tests.json | \
      python3 -m testdrive.junit --prettify "examples.sequence" -
    <?xml version='1.0' encoding='utf-8'?>
    <testsuites tests="3" errors="0" failures="2" skipped="0">
      <testsuite name="examples.sequence" tests="3" errors="0" failures="2" skipped="0" timestamp="2023-08-25T10:45:51.061162+00:00" time="0.078068">
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/A/" time="0.047357">
          <failure type="Failure" message="something went wrong" />
          <system-out>{
        "argv": [],
        "data": {
            "foo": "bar"
        },
        "reason": "something went wrong",
        "result": false
    }</system-out>
          <properties>
            <property name="test_id" value="https://github.com/redhat-partner-solutions/testdrive/A/" />
          </properties>
        </testcase>
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/B/" time="0.025998">
          <system-out>{
        "argv": [],
        "data": {
            "baz": 99
        },
        "reason": null,
        "result": true
    }</system-out>
          <properties>
            <property name="test_id" value="https://github.com/redhat-partner-solutions/testdrive/B/" />
          </properties>
        </testcase>
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/C/" time="0.004589">
          <failure type="Failure" message="no particular reason" />
          <system-out>{
        "argv": [],
        "reason": "no particular reason",
        "result": false
    }</system-out>
          <properties>
            <property name="test_id" value="https://github.com/redhat-partner-solutions/testdrive/C/" />
          </properties>
        </testcase>
      </testsuite>
    </testsuites>

## testdrive.xml

Module `testdrive.xml` provides a basic XML validator. This, along with the
schema file `junit/schema/testdrive.xsd`, is provided in order to test the
output from `testdrive.junit` and to allow comparison with Windy Road JUnit
schema `junit/schema/junit.xsd`.

The following JUnit output from testdrive...

    $ cat results.xml
    <?xml version='1.0' encoding='utf-8'?>
    <testsuites tests="3" errors="0" failures="2" skipped="0">
      <testsuite name="examples.sequence" tests="3" errors="0" failures="2" skipped="0" timestamp="2023-08-25T10:45:51.061162+00:00" time="0.078068">
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/A/" time="0.047357">
          <failure type="Failure" message="something went wrong" />
          <system-out>{
        "argv": [],
        "data": {
            "foo": "bar"
        },
        "reason": "something went wrong",
        "result": false
    }</system-out>
          <properties>
            <property name="test_id" value="https://github.com/redhat-partner-solutions/testdrive/A/" />
          </properties>
        </testcase>
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/B/" time="0.025998">
          <system-out>{
        "argv": [],
        "data": {
            "baz": 99
        },
        "reason": null,
        "result": true
    }</system-out>
          <properties>
            <property name="test_id" value="https://github.com/redhat-partner-solutions/testdrive/B/" />
          </properties>
        </testcase>
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/C/" time="0.004589">
          <failure type="Failure" message="no particular reason" />
          <system-out>{
        "argv": [],
        "reason": "no particular reason",
        "result": false
    }</system-out>
          <properties>
            <property name="test_id" value="https://github.com/redhat-partner-solutions/testdrive/C/" />
          </properties>
        </testcase>
      </testsuite>
    </testsuites>

...validates using the testdrive JUnit schema...

    $ python3 -m testdrive.xml junit/schema/testdrive.xsd results.xml
    <?xml version='1.0' encoding='utf-8'?>
    <testsuites tests="3" errors="0" failures="2" skipped="0">
      <testsuite name="examples.sequence" tests="3" errors="0" failures="2" skipped="0" timestamp="2023-08-25T10:45:51.061162+00:00" time="0.078068">
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/A/" time="0.047357">
          <failure type="Failure" message="something went wrong" />
          <system-out>{
        "argv": [],
        "data": {
            "foo": "bar"
        },
        "reason": "something went wrong",
        "result": false
    }</system-out>
          <properties>
            <property name="test_id" value="https://github.com/redhat-partner-solutions/testdrive/A/" />
          </properties>
        </testcase>
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/B/" time="0.025998">
          <system-out>{
        "argv": [],
        "data": {
            "baz": 99
        },
        "reason": null,
        "result": true
    }</system-out>
          <properties>
            <property name="test_id" value="https://github.com/redhat-partner-solutions/testdrive/B/" />
          </properties>
        </testcase>
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/C/" time="0.004589">
          <failure type="Failure" message="no particular reason" />
          <system-out>{
        "argv": [],
        "reason": "no particular reason",
        "result": false
    }</system-out>
          <properties>
            <property name="test_id" value="https://github.com/redhat-partner-solutions/testdrive/C/" />
          </properties>
        </testcase>
      </testsuite>
    </testsuites>

...and _does not_ validate using the Windy Road JUnit schema:

    $ python3 -m testdrive.xml --verbose junit/schema/junit.xsd results.xml

    failed validating {'tests': '3', 'errors': '0', 'failures': '2', 'skipped': '0'} with XsdAttributeGroup():

    Reason: 'tests' attribute not allowed for element

    Schema:

      <xs:complexType xmlns:xs="http://www.w3.org/2001/XMLSchema">
          <xs:sequence>
              <xs:element name="testsuite" minOccurs="0" maxOccurs="unbounded">
                  <xs:complexType>
                      <xs:complexContent>
                          <xs:extension base="testsuite">
                              <xs:attribute name="package" type="xs:token" use="required">
                                  <xs:annotation>
                                      <xs:documentation xml:lang="en">Derived from testsuite/@name in the non-aggregated documents</xs:documentation>
                                  </xs:annotation>
                              </xs:attribute>
                              <xs:attribute name="id" type="xs:int" use="required">
                                  <xs:annotation>
                                      <xs:documentation xml:lang="en">Starts at '0' for the first testsuite and is incremented by 1 for each following testsuite</xs:documentation>
                                  </xs:annotation>
                              </xs:attribute>
                          </xs:extension>
                      </xs:complexContent>
                  </xs:complexType>
              </xs:element>
          </xs:sequence>
      </xs:complexType>

    Instance:

      <testsuites tests="3" errors="0" failures="2" skipped="0">
        <testsuite name="examples.sequence" tests="3" errors="0" failures="2" skipped="0" timestamp="2023-08-25T10:45:51.061162+00:00" time="0.078068">
          <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/A/" time="0.047357">
            <failure type="Failure" message="something went wrong" />
            <system-out>{
          "argv": [],
          "data": {
              "foo": "bar"
          },
          "reason": "something went wrong",
          "result": false
      }</system-out>
            <properties>
              <property name="test_id" value="https://github.com/redhat-partner-solutions/testdrive/A/" />
            </properties>
          </testcase>
          <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/B/" time="0.025998">
            <system-out>{
          "argv": [],
          "data": {
      ...
      ...
      </testsuites>

    Path: /testsuites

To see the differences between the schemas, simply use diff:

    $ diff junit/schema/junit.xsd junit/schema/testdrive.xsd
    7c7,16
    < 		<xs:documentation xml:lang="en">JUnit test result schema for the Apache Ant JUnit and JUnitReport tasks
    ---
    > 		<!-- modified: complement original documentation -->
    > 		<xs:documentation xml:lang="en">A schema for testdrive JUnit test results.
    > 
    > testdrive emits test results which are not strictly compatible with the Windy
    > Road JUnit schema (because the CI systems which consume these results are not
    > strictly compatible). This schema is a modified version of the Windy Road JUnit
    > schema, for which the original text in this element is retained below.
    > 
    > -----
    > JUnit test result schema for the Apache Ant JUnit and JUnitReport tasks
    11a21,36
    > 
    > 	<!-- modified: define properties, property elements -->
    > 	<xs:element name="properties">
    > 		<xs:complexType>
    > 			<xs:sequence>
    > 				<xs:element ref="property" minOccurs="0" maxOccurs="unbounded"/>
    > 			</xs:sequence>
    > 		</xs:complexType>
    > 	</xs:element>
    > 	<xs:element name="property">
    ...

## testdrive.asciidoc

Module `testdrive.asciidoc` can be used to generate [Asciidoc][3] test results
from lines of JSON (one line per test case result):

    $ python3 -m testdrive.run https://github.com/redhat-partner-solutions/testdrive/ examples/sequence/tests.json | \
      python3 -m testdrive.asciidoc "examples.sequence" - | tee results.adoc
    === Test Suite: examples.sequence

    ==== Summary

    [cols=2*.^a]
    |===


    |
    *hostname*
    |
    _not known_

    |
    *started*
    |
    2023-07-31T13:29:08.844977+00:00
    ...

To include this in a simple report:

    $ cat report.adoc
    = Test Report

    :toc:

    == Test Results

    <<<
    include::results.adoc[]

    $ asciidoctor -a toc report.adoc && firefox report.html

[1]: https://www.distributed-ci.io/
[2]: https://github.com/redhat-partner-solutions/testdrive/blob/cce8fb30bd8eed8e83f53665cd1433e20c81cfd3/src/testdrive/run.py#L60
[3]: https://docs.asciidoctor.org/asciidoc/latest/
