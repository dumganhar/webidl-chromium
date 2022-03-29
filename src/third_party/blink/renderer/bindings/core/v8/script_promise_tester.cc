// Copyright 2019 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "third_party/blink/renderer/bindings/core/v8/script_promise_tester.h"

#include <utility>

#include "third_party/blink/renderer/bindings/core/v8/script_function.h"
#include "third_party/blink/renderer/bindings/core/v8/script_promise.h"
#include "third_party/blink/renderer/platform/bindings/script_state.h"
#include "third_party/blink/renderer/platform/heap/garbage_collected.h"
#include "third_party/blink/renderer/platform/testing/unit_test_helpers.h"
#include "v8/include/v8.h"

namespace blink {

class ScriptPromiseTester::ThenFunction : public ScriptFunction::Callable {
 public:
  ThenFunction(base::WeakPtr<ScriptPromiseTester> owner,
               ScriptPromiseTester::State target_state)
      : owner_(std::move(owner)), target_state_(target_state) {}

  ScriptValue Call(ScriptState*, ScriptValue value) override {
    if (!owner_)
      return value;

    DCHECK_EQ(owner_->state_, State::kNotSettled);
    owner_->state_ = target_state_;

    DCHECK(owner_->value_.IsEmpty());
    owner_->value_ = value;
    return value;
  }

 private:
  base::WeakPtr<ScriptPromiseTester> owner_;
  State target_state_;
};

ScriptPromiseTester::ScriptPromiseTester(ScriptState* script_state,
                                         ScriptPromise script_promise)
    : script_state_(script_state) {
  DCHECK(script_state);
  script_promise.Then(
      MakeGarbageCollected<ScriptFunction>(
          script_state, MakeGarbageCollected<ThenFunction>(
                            weak_factory_.GetWeakPtr(), State::kFulfilled)),
      MakeGarbageCollected<ScriptFunction>(
          script_state, MakeGarbageCollected<ThenFunction>(
                            weak_factory_.GetWeakPtr(), State::kRejected)));
}

void ScriptPromiseTester::WaitUntilSettled() {
  auto* isolate = script_state_->GetIsolate();
  while (state_ == State::kNotSettled) {
    v8::MicrotasksScope::PerformCheckpoint(isolate);
    test::RunPendingTasks();
  }
}

ScriptValue ScriptPromiseTester::Value() const {
  return value_;
}

void ScriptPromiseTester::Trace(Visitor* visitor) const {
  visitor->Trace(script_state_);
  visitor->Trace(value_);
}

}  // namespace blink
