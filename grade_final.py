import os
import sys
import subprocess
import shutil
import xml.etree.ElementTree as ET
import csv
import pandas as pd
import json
import glob
from collections import Counter
from datetime import datetime
import time
import hashlib

# base_directory = "/Users/kianenigma/Desktop/Parity/pba4/hk-2024-assignment-3-frameless-submissions"
base_directory = "/Users/akon/github/pba-private/hk-2024-assignment-3-frameless-submissions"
prefix = "hk-2024-assignment-3-frameless"


def build_wasms():
    wasm_hash_set = set()
    for folder in os.listdir(base_directory):
        if not maybe_filter(folder):
            continue

        student_folder = os.path.join(base_directory, folder)

        # checkout to branch main, if not already there.
        subprocess.run(
            ["git", "checkout", "main"],
            cwd=student_folder,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            check=True,
        )

        # if a wasm file already exists at student_folder + wasm, skip to next folder.
        if os.path.exists(os.path.join(student_folder, "runtime.wasm")):
            # calculate the md5 checksum by reading the file
            with open(os.path.join(student_folder, "runtime.wasm"), "rb") as f:
                checksum = hashlib.md5(f.read()).hexdigest()
                if checksum in wasm_hash_set:
                    print(
                        f"⚠️ {student_folder} has a duplicate runtime.wasm md5 hash {checksum}"
                    )

                wasm_hash_set.add(checksum)
                print(
                    f"🎉 {student_folder} already has a runtime.wasm ({checksum}), skipping to next folder."
                )
                continue

        print(f"👷 building {student_folder}")

        # pipe stderr such that it gets displayed in just one line, updating as new things happen.
        build_status = subprocess.run(
            ["cargo", "build", "--release", "-p", "runtime"],
            cwd=student_folder,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )

        # if build_status was not success, print and skip
        if build_status.returncode != 0:
            print(f"⚠️ {student_folder} failed to build, skipping to next folder.")
            continue

        # copy the wasm file to the root of the folder.
        wasm_file_path = os.path.join(
            student_folder, "target", "release", "wbuild", "runtime", "runtime.wasm"
        )
        if os.path.exists(wasm_file_path):
            shutil.copy(wasm_file_path, os.path.join(student_folder, "runtime.wasm"))
            print(f"✅ built {wasm_file_path}")
        else:
            print(f"⚠️ {wasm_file_path} does not exist, skipping to next folder.")
            continue

    for folder in os.listdir(base_directory):
        if not maybe_filter(folder):
            continue

        # run cargo clean in each folder.
        student_folder = os.path.join(base_directory, folder)

        subprocess.run(
            ["cargo", "clean"],
            cwd=student_folder,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            check=True,
        )

    print("🎉 done building wasm files and all clean.")


def test_count(test):
    output = subprocess.run(
        [
            "cargo",
            "nextest",
            "list",
            "-p",
            "runtime",
            "--features",
            "final-grade",
            "-E",
            f"test({test})",
            "-T",
            "json-pretty",
        ],
        cwd=".",
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        check=True,
    )
    # the output of this is a JSON object. parse it as dict, and get obj['rust-suites']['runtime]['testcases]
    testcases = json.loads(output.stdout.decode("utf-8"))["rust-suites"][
        "runtime::grading"
    ]["testcases"]

    count = 0
    for testcase in testcases:
        if testcases[testcase]["filter-match"]["status"] == "matches":
            count += 1
    return count


def maybe_filter(folder):
    if folder.startswith(prefix):
        if len(sys.argv) > 1:
            if sys.argv[1] not in folder:
                print(f"🏹 {sys.argv[1]} not in {folder}, skipping to next folder.")
                return False
        return True
    else:
        print(f"🏹 {prefix} not in {folder}, skipping to next folder.")
        return False


basics_fundamentals_test_count = test_count("basics::fundamentals")
basics_challenging_test_count = test_count("basics::challenging")
basics_optional_test_count = test_count("basics::optional")

currency_fundamentals_test_count = test_count("currency::fundamentals")
currency_challenging_test_count = test_count("currency::challenging")
currency_optional_test_count = test_count("currency::optional")

staking_fundamentals_test_count = test_count("staking::fundamentals")
staking_challenging_test_count = test_count("staking::challenging")
staking_optional_test_count = test_count("staking::optional")

tipping_fundamentals_test_count = test_count("tipping::fundamentals")
tipping_challenging_test_count = test_count("tipping::challenging")
tipping_optional_test_count = test_count("tipping::optional")

nonce_fundamentals_test_count = test_count("nonce::fundamentals")
nonce_challenging_test_count = test_count("nonce::challenging")
nonce_optional_test_count = test_count("nonce::optional")

basics_max_fundamentals_failures = 0
basics_max_challenging_failure = 2

currency_max_fundamentals_failures = 0
currency_max_challenging_failure = 4

staking_max_fundamentals_failures = 0
staking_max_challenging_failure = 2

tipping_max_fundamentals_failures = 0
tipping_max_challenging_failure = 4

nonce_max_fundamentals_failures = 0
nonce_max_challenging_failure = 2

distinction_max_failures = 5

# for each category of tests, print the count, and the max allowed failures.
print(
    f"""
basics::fundamentals: {basics_fundamentals_test_count}, max_failures: {basics_max_fundamentals_failures}
basics::challenging: {basics_challenging_test_count}, max_failures: {basics_max_challenging_failure}
basics::optional: {basics_optional_test_count},
currency::fundamentals: {currency_fundamentals_test_count}, max_failures: {currency_max_fundamentals_failures}
currency::challenging: {currency_challenging_test_count}, max_failures: {currency_max_challenging_failure}
currency::optional: {currency_optional_test_count},
staking::fundamentals: {staking_fundamentals_test_count}, max_failures: {staking_max_fundamentals_failures}
staking::challenging: {staking_challenging_test_count}, max_failures: {staking_max_challenging_failure}
staking::optional: {staking_optional_test_count},
tipping::fundamentals: {tipping_fundamentals_test_count}, max_failures: {tipping_max_fundamentals_failures}
tipping::challenging: {tipping_challenging_test_count}, max_failures: {tipping_max_challenging_failure}
tipping::optional: {tipping_optional_test_count},
nonce::fundamentals: {nonce_fundamentals_test_count}, max_failures: {nonce_max_fundamentals_failures}
nonce::challenging: {nonce_challenging_test_count}, max_failures: {nonce_max_challenging_failure}
nonce::optional: {nonce_optional_test_count},
"""
)

failure_counter = Counter()


def grade_test_module(folder, test_prefix, max_failures):
    student_folder = os.path.join(base_directory, folder)
    wasm_file_path = os.path.join(student_folder, "runtime.wasm")
    student_result_folder = os.path.join(student_folder, "result")

    if not os.path.exists(wasm_file_path):
        print(f"⚠️ {wasm_file_path} does not exist, error.")
        exit(1)

    if not os.path.exists(student_result_folder):
        os.mkdir(student_result_folder)

    stderr_file = open(f"{student_result_folder}/{test_prefix}_stderr.txt", "w")

    custom_env = os.environ.copy()
    custom_env["RUST_LOG"] = "grading=debug"
    custom_env["WASM_FILE"] = wasm_file_path

    test_proc_code = subprocess.run(
        [
            "cargo",
            "nextest",
            "run",
            "--release",
            "-p",
            "runtime",
            "--features",
            "final-grade",
            "-E" f"test({test_prefix})",
            "--failure-output",
            "final",
            "--success-output",
            "never",
            "--no-fail-fast",
        ],
        env=custom_env,
        cwd=".",
        stderr=stderr_file,
        stdout=subprocess.PIPE,
        check=False,
    ).returncode

    # copy the xml file to root for better visibility:
    xml_file_path = os.path.join("target", "nextest", "default", "result.xml")
    shutil.copy(
        xml_file_path, os.path.join(student_result_folder, f"{test_prefix}_result.xml")
    )

    tree = ET.parse(f"{student_result_folder}/{test_prefix}_result.xml")
    root = tree.getroot()
    # Find all 'testsuite' elements under 'testsuites'
    test_cases = root.findall("./testsuite/testcase")
    test_cases_len = len(test_cases)

    if test_cases_len == 0:
        return {
            "outcome": True,
            "failures": [],
            "successes": [],
            "summary": f"🤷 no tests in {test_prefix} subgroup.",
        }

    failures = []
    successes = []
    for test in test_cases:
        failure = test.find("failure")

        if failure is not None:
            failures.append(test.attrib["name"])
        else:
            successes.append(test.attrib["name"])

    failures_len = len(failures)
    successes_len = len(successes)
    if failures_len > max_failures:
        emoji = "🤷" if "optional" in test_prefix else "❌"
        summary = f"{emoji} failed {test_prefix} with {successes_len}/{test_cases_len} successes."
        print(f"  {summary}")
        return {
            "outcome": False,
            "failures": failures,
            "successes": successes,
            "summary": summary,
        }
    else:
        emoji = "👍" if "optional" in test_prefix else "✅"
        summary = f"{emoji} passed {test_prefix} with {successes_len}/{test_cases_len} successes."
        print(f"  {summary}")
        return {
            "outcome": True,
            "failures": failures,
            "successes": successes,
            "summary": summary,
        }


def grade_student(folder, writer):
    student_name = folder.split("less")[1][1:].strip()
    print("👷 grading", student_name)
    start_time = time.time()

    b1 = grade_test_module(
        folder, "basics::fundamentals", basics_max_fundamentals_failures
    )
    b2 = grade_test_module(folder, "basics::challenging", basics_max_challenging_failure)
    b3 = grade_test_module(folder, "basics::optional", 0)
    basics = b1["outcome"] and b2["outcome"]
    failure_counter.update(b1["failures"] + b2["failures"] + b3["failures"])

    c1 = grade_test_module(
        folder, "currency::fundamentals", currency_max_fundamentals_failures
    )
    c2 = grade_test_module(folder, "currency::challenging", currency_max_challenging_failure)
    c3 = grade_test_module(folder, "currency::optional", 0)
    currency = c1["outcome"] and c2["outcome"]
    failure_counter.update(c1["failures"] + c2["failures"] + c3["failures"])

    t1 = grade_test_module(
        folder, "tipping::fundamentals", tipping_max_fundamentals_failures
    )
    t2 = grade_test_module(folder, "tipping::challenging", tipping_max_challenging_failure)
    t3 = grade_test_module(folder, "tipping::optional", 0)
    tipping = t1["outcome"] and t2["outcome"]
    failure_counter.update(t1["failures"] + t2["failures"] + t3["failures"])

    n1 = grade_test_module(
        folder, "nonce::fundamentals", nonce_max_fundamentals_failures
    )
    n2 = grade_test_module(folder, "nonce::challenging", nonce_max_challenging_failure)
    n3 = grade_test_module(folder, "nonce::optional", 0)
    nonce = n1["outcome"] and n2["outcome"]
    failure_counter.update(n1["failures"] + n2["failures"] + n3["failures"])

    s1 = grade_test_module(
        folder, "staking::fundamentals", staking_max_fundamentals_failures
    )
    s2 = grade_test_module(folder, "staking::challenging", staking_max_challenging_failure)
    s3 = grade_test_module(folder, "staking::optional", 0)
    staking = s1["outcome"] and s2["outcome"]
    failure_counter.update(s1["failures"] + s2["failures"] + s3["failures"])

    tipping_or_nonce = tipping or nonce

    auto_grade = int(basics) + int(currency) + int(tipping_or_nonce)
    end_time = time.time()
    elapsed_time = end_time - start_time

    # calculate the sum of successes from all items
    sum_successes = (
            len(b1["successes"])
            + len(b2["successes"])
            + len(b3["successes"])
            + len(c1["successes"])
            + len(c2["successes"])
            + len(c3["successes"])
            + len(s1["successes"])
            + len(s2["successes"])
            + len(s3["successes"])
            + len(t1["successes"])
            + len(t2["successes"])
            + len(t3["successes"])
            + len(n1["successes"])
            + len(n2["successes"])
            + len(n3["successes"])
    )
    sum_failures = (
            len(b1["failures"])
            + len(b2["failures"])
            + len(b3["failures"])
            + len(c1["failures"])
            + len(c2["failures"])
            + len(c3["failures"])
            + len(s1["failures"])
            + len(s2["failures"])
            + len(s3["failures"])
            + len(t1["failures"])
            + len(t2["failures"])
            + len(t3["failures"])
            + len(n1["failures"])
            + len(n2["failures"])
            + len(n3["failures"])
    )

    distinction = "😞 No distinction." if sum_failures > distinction_max_failures else "🔥 Received distinction."
    if sum_failures <= distinction_max_failures:
        auto_grade += 1

    print(f"  {distinction}")

    final_summary = f"sum-success: {sum_successes} / sum-failure: {sum_failures} / auto-graded-score: {auto_grade}, grading time: {elapsed_time:.2f}s"
    print(f"\033[1m {final_summary} \033[0m")

    writer.writerow(
        [
            student_name,
            auto_grade,
            sum_successes,
            sum_failures,
            len(b1["successes"]),
            len(b2["successes"]),
            len(b3["successes"]),
            len(c1["successes"]),
            len(c2["successes"]),
            len(c3["successes"]),
            len(s1["successes"]),
            len(s2["successes"]),
            len(s3["successes"]),
            len(t1["successes"]),
            len(t2["successes"]),
            len(t3["successes"]),
            len(n1["successes"]),
            len(n2["successes"]),
            len(n3["successes"]),
        ]
    )

    # TODO: update this. Be very clear on the rubric. Quote what was already posted on discord.

    # TODO: All hidden tests are spread into the challenging/optional. This should give students
    # less excuse to fail any of the existing fundamental tests. Although, they could say that it
    # was not said to them that failing 1 test might cause them to fail the whole section.

    final_grade_template = f"""## Prelude

First, congratulations on completing this assignment. Please bear in mind that this assignment was
significantly more challenging, and open ended than the previous two. Be proud of your learning.

## Wasm File

If you provided a `runtime.wasm` in the root of your main branch, we used that. Else, we ran `cargo
run --release -p runtime` and used the output. This has no effect on your score.

## Grading Process

<details>

<summary>Click to see the detailed grading process.</summary>

This grading report is generated based on the grading guidelines that you were given at the start of
the assignment. Recall that our tests are broadly categorized into 3 groups:

* if you pass all the _basics_ tests, you get 1 point.
* if you pass all the _currency_ tests, you get 1 point.
* if you pass either all the _tipping *OR* nonce_ tests, you get 1 point.

Your instructors will also provide a manual review of your code, but this does not impact your 
score.

In each testing group, there are 3 subgroups. In each subgroup, you are allowed a maximum number of
test failures. The subgroups, and their respective maximum number of allowed failures are:

* **fundamentals**: you are allowed to have no failures in this subgroup.
* **challenging**: you are allowed to have a number of failures in this subgroup. These are
    tests that are more challenging, and we expect you to get some of them wrong, but not all.
* **optional**: you are allowed to have any number of failures here, and it will have
    no impact on your auto-computed score. These are edge cases that we didn't expect you to get
    correctly, because the assignment didn't clarify them.

Note that some of the tests were hidden in the pre-grading process. None of these tests ended up
being in the "fundamentals" group, so you had at least 5 trials (pregrades) to make sure you get the
fundamentals correct in each category.

### Distinction

Additionally, we impose the following requirements for receiving a distinction:
* You received 3 points from above requirements, and
* You only fail upto maximum of {distinction_max_failures} tests.

You can identify the _group_ and _subgroup_ of each tests by looking at the name of the test. For
example:

``` tipping::fundamentals::alice_with_u128_max_div2_tips_u128_max_div4 ```

Is a test in the tipping group, and _fundamentals_ subgroup.

To summarize, the number of tests, and max failures for each subgroup are as follows:

* basics:
        * {basics_fundamentals_test_count} fundamental tests, {basics_max_fundamentals_failures} max failures.
        * {basics_challenging_test_count} challenging tests, {basics_max_challenging_failure} max failures.
        * {nonce_optional_test_count} optional tests.
* currency:
        * {currency_fundamentals_test_count} fundamental tests, {currency_max_fundamentals_failures} max failures.
        * {currency_challenging_test_count} challenging tests, {currency_max_challenging_failure} max failures.
        * {currency_optional_test_count} optional tests.
* tipping:
        * {tipping_fundamentals_test_count} fundamental tests, {tipping_max_fundamentals_failures} max failures.
        * {tipping_challenging_test_count} challenging tests, {tipping_max_challenging_failure} max failures.
        * {tipping_optional_test_count} optional tests.
* nonce:
        * {nonce_fundamentals_test_count} fundamental tests, {nonce_max_fundamentals_failures} max failures.
        * {nonce_challenging_test_count} challenging tests, {nonce_max_challenging_failure} max failures.
        * {nonce_optional_test_count} optional tests.
* staking:
        * {staking_fundamentals_test_count} fundamental tests, {staking_max_fundamentals_failures} max failures.
        * {staking_challenging_test_count} challenging tests, {staking_max_challenging_failure} max failures.
        * {staking_optional_test_count} optional tests.
* distinction:
        * Less than or equal to {distinction_max_failures} failures overall.        

As seen, all staking tests are marked as optional and have no impact on your score.

</details>

## Auto-Graded Score

* basics
        * {b1['summary']}
        * {b2['summary']}
        * {b3['summary']}
* currency
        * {c1['summary']}
        * {c2['summary']}
        * {c3['summary']}
* tipping
        * {t1['summary']}
        * {t2['summary']}
        * {t3['summary']}
* nonce
        * {n1['summary']}
        * {n2['summary']}
        * {n3['summary']}
* staking
        * {s1['summary']}
        * {s2['summary']}
        * {s3['summary']}
* distinction
        * {distinction}         

{final_summary}

Other than this report, you also receive the `xml` and `stderr` file if your entire test run in the
`result` folder pushed to this branch.

## Manual Review

Please see the feedback PR in your repo for potential further comments. Your instructors will leave
a series of comments there, in the style of a pull request review.

## Score

**{auto_grade}**

"""

    student_folder = os.path.join(base_directory, folder)
    with open(f"{student_folder}/result.md", "w") as f:
        f.write(final_grade_template)


def calculate_final_grades():
    csv_cols = [
        "student",
        "final-score",
        "sum-success",
        "sum-failures",
        f"basics::fundamentals ({basics_fundamentals_test_count})",
        f"basics::challenging ({basics_challenging_test_count}, max_failures: {basics_max_challenging_failure})",
        f"basics::optional ({basics_optional_test_count})",
        f"currency::fundamentals ({currency_fundamentals_test_count})",
        f"currency::challenging ({currency_challenging_test_count}, max_failures: {currency_max_challenging_failure})",
        f"currency::optional ({currency_optional_test_count})",
        f"staking::fundamentals ({staking_fundamentals_test_count})",
        f"staking::challenging ({staking_challenging_test_count}, max_failures: {staking_max_challenging_failure})",
        f"staking::optional ({staking_optional_test_count})",
        f"tipping::fundamentals ({tipping_fundamentals_test_count})",
        f"tipping::challenging ({tipping_challenging_test_count}, max_failures: {tipping_max_challenging_failure})",
        f"tipping::optional ({tipping_optional_test_count})",
        f"nonce::fundamentals ({nonce_fundamentals_test_count})",
        f"nonce::challenging ({nonce_challenging_test_count}, max_failures: {nonce_max_challenging_failure})",
        f"nonce::optional ({nonce_optional_test_count})",
    ]

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    results_filename = f"{timestamp}_results.csv"
    tests_filename = f"{timestamp}_tests.csv"

    with open(results_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(csv_cols)

        for folder in os.listdir(base_directory):
            if not maybe_filter(folder):
                continue
            grade_student(folder, writer)
            f.flush()

    with open(tests_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["test", "failures"])
        for test, count in failure_counter.most_common():
            writer.writerow([test, count])


def analyze_csv_output():
    csv_files = glob.glob("*results.csv")
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)

        bins = [0, 1, 2, 3, 4]

        df["binned"] = pd.cut(df["final-score"], bins, include_lowest=True, right=False)
        histogram = df["binned"].value_counts()
        histogram.sort_index(inplace=True)

        df.drop(columns=["student"], axis=1, inplace=True)
        with open(csv_file.replace("results.csv", "summary.txt"), "w") as f:
            f.write(df.describe().to_string())
            f.write("\n\n")
            f.write(histogram.to_string())


def push_grades(actually_push):
    for folder in os.listdir(base_directory):
        if not maybe_filter(folder):
            continue

        student_folder = os.path.join(base_directory, folder)

        # checkout to a branch called `grade`
        subprocess.run(
            ["git", "checkout", "-B", "grade"],
            cwd=student_folder,
            check=True,
        )
        subprocess.run(
            ["git", "add", "result.md"],
            cwd=student_folder,
            check=True,
        )
        subprocess.run(
            ["git", "add", "result/"],
            cwd=student_folder,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "autograding"],
            cwd=student_folder,
            check=True,
        )

        # push
        if actually_push:
            subprocess.run(
                ["git", "push", "origin", "grade"],
                cwd=student_folder,
                check=True,
            )

            with open(f"{student_folder}/result.md", "r") as f:
                result = f.read()
                subprocess.run(
                    ["gh", "pr", "create", "--title", "Grade", "--body", result],
                    cwd=student_folder,
                    check=True,
                )


def clear_all_artifacts():
    for folder in os.listdir(base_directory):
        if not maybe_filter(folder):
            continue

        student_folder = os.path.join(base_directory, folder)

        # delete `result.md` and `result/` folder
        subprocess.run(
            ["rm", "-rf", "result.md"],
            cwd=student_folder,
            check=True,
        )
        subprocess.run(
            ["rm", "-rf", "./result"],
            cwd=student_folder,
            check=True,
        )


if __name__ == "__main__":
    # build_wasms()
    clear_all_artifacts()
    calculate_final_grades()
    analyze_csv_output()
    # push_grades(False)
    print("Done!")
