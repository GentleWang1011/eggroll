/*
 * Copyright (c) 2019 - now, Eggroll Authors. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.webank.ai.eggroll.core.factory;

import com.google.common.base.Preconditions;
import com.webank.ai.eggroll.core.di.Singletons;
import com.webank.ai.eggroll.core.model.Endpoint;
import io.grpc.ManagedChannel;
import io.grpc.stub.AbstractStub;
import java.lang.reflect.InvocationTargetException;
import org.apache.commons.lang3.reflect.MethodUtils;

public class GrpcStubFactory {

  private static final String asyncStubMethodName = "newStub";
  private static final String blockingStubMethodName = "newBlockingStub";

  private GrpcChannelFactory grpcChannelFactory;

  public GrpcStubFactory() {
    grpcChannelFactory = Singletons.getNoCheck(GrpcChannelFactory.class);
  }

  public AbstractStub createGrpcStub(boolean isAsync, Class grpcClass,
      ManagedChannel managedChannel) {
    String methodName = null;
    if (isAsync) {
      methodName = asyncStubMethodName;
    } else {
      methodName = blockingStubMethodName;
    }

    AbstractStub result = null;
    try {
      result = (AbstractStub) MethodUtils
          .invokeStaticMethod(grpcClass, methodName, managedChannel);
    } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
      throw new RuntimeException("error creating stub", e);
    }

    return result;
  }

  public AbstractStub createGrpcStub(boolean isAsync, Class grpcClass, Endpoint endpoint,
      boolean isSecure) {
    Preconditions.checkNotNull(endpoint, "Endpoint cannot be null");
    ManagedChannel managedChannel = grpcChannelFactory.getChannel(endpoint, isSecure);

    return createGrpcStub(isAsync, grpcClass, managedChannel);
  }
}
